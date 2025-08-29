import six
from django.apps import apps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.db.utils import NotSupportedError
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.defaults import bad_request
from django.views.generic import ListView
from django_comments.models import CommentFlag
from django_comments.signals import comment_was_posted, comment_will_be_posted
from django_comments.views.moderation import perform_flag
from django_comments.views.utils import confirmation_view, next_redirect

from django_comments_xtd import get_form, signals, signed
from django_comments_xtd import get_model as get_comment_model
from django_comments_xtd.conf import settings
from django_comments_xtd.models import (
    DISLIKEDIT_FLAG,
    LIKEDIT_FLAG,
    MaxThreadLevelExceededException,
    TmpXtdComment,
)
from django_comments_xtd.utils import (
    get_app_model_options,
    get_current_site_id,
    send_mail,
)

XtdComment = get_comment_model()


def get_moderated_tmpl(cmt):
    return [
        (
            f"django_comments_xtd/{cmt.content_type.app_label}"
            f"/{cmt.content_type.model}/moderated.html"
        ),
        f"django_comments_xtd/{cmt.content_type.app_label}/moderated.html",
        "django_comments_xtd/moderated.html",
    ]


def send_email_confirmation_request(
    comment,
    key,
    site,
    text_template="django_comments_xtd/email_confirmation_request.txt",
    html_template="django_comments_xtd/email_confirmation_request.html",
):
    """Send email requesting comment confirmation"""
    subject = _("comment confirmation request")
    confirmation_url = reverse(
        "comments-xtd-confirm", args=[key.decode("utf-8")]
    )
    message_context = {
        "comment": comment,
        "confirmation_url": confirmation_url,
        "contact": settings.COMMENTS_XTD_CONTACT_EMAIL,
        "site": site,
    }
    # prepare text message
    text_message_template = loader.get_template(text_template)
    text_message = text_message_template.render(message_context)
    if settings.COMMENTS_XTD_SEND_HTML_EMAIL:
        # prepare html message
        html_message_template = loader.get_template(html_template)
        html_message = html_message_template.render(message_context)
    else:
        html_message = None

    send_mail(
        subject,
        text_message,
        settings.COMMENTS_XTD_FROM_EMAIL,
        [
            comment.user_email,
        ],
        html=html_message,
    )


def _get_comment_if_exists(comment):
    """
    True if exists a XtdComment with same user_name, user_email and submit_date.
    """
    return XtdComment.objects.filter(
        user_name=comment.user_name,
        user_email=comment.user_email,
        followup=comment.followup,
        submit_date=comment.submit_date,
    ).first()


def _create_comment(tmp_comment):
    """
    Creates a XtdComment from a TmpXtdComment.
    """
    comment = XtdComment(**tmp_comment)
    # comment.is_public = True
    comment.save()
    return comment


def on_comment_will_be_posted(sender, comment, request, **kwargs):
    """
    Check whether there are conditions to reject the post.

    Returns False if there are conditions to reject the comment.
    """
    if settings.COMMENTS_APP != "django_comments_xtd":
        # Do not kill the post if handled by other commenting app.
        return True

    if comment.user:
        user_is_authenticated = comment.user.is_authenticated
    else:
        user_is_authenticated = False

    options = get_app_model_options(comment=comment)

    return not (  # Return False to reject comment.
        options["who_can_post"] == "users" and not user_is_authenticated
    )


comment_will_be_posted.connect(on_comment_will_be_posted, sender=TmpXtdComment)


def on_comment_was_posted(sender, comment, request, **kwargs):
    """
    Post the comment if a user is authenticated or send a confirmation email.

    On signal django_comments.signals.comment_was_posted check if the
    user is authenticated or if settings.COMMENTS_XTD_CONFIRM_EMAIL is False.
    In both cases will post the comment. Otherwise will send a confirmation
    email to the person who posted the comment.
    """
    if settings.COMMENTS_APP != "django_comments_xtd":
        return False
    if comment.user:
        user_is_authenticated = comment.user.is_authenticated
    else:
        user_is_authenticated = False

    if not settings.COMMENTS_XTD_CONFIRM_EMAIL or user_is_authenticated:
        if _get_comment_if_exists(comment) is None:
            new_comment = _create_comment(comment)
            comment.xtd_comment = new_comment
            signals.confirmation_received.send(
                sender=TmpXtdComment, comment=comment, request=request
            )
            if comment.is_public:
                notify_comment_followers(new_comment)
    else:
        key = signed.dumps(
            comment, compress=True, extra_key=settings.COMMENTS_XTD_SALT
        )
        site = get_current_site(request)
        send_email_confirmation_request(comment, key, site)


comment_was_posted.connect(on_comment_was_posted, sender=TmpXtdComment)


def sent(request, using=None):
    comment_pk = request.GET.get("c", None)
    if not comment_pk:
        return HttpResponseBadRequest("Comment doesn't exist")

    try:
        comment_pk = int(comment_pk)
        comment = XtdComment.objects.get(pk=comment_pk)
    except (TypeError, ValueError, XtdComment.DoesNotExist):
        try:
            value = signing.loads(comment_pk)
            ctype, object_pk = value.split(":")
            model = apps.get_model(*ctype.split(".", 1))
            target = model._default_manager.using(using).get(pk=object_pk)
        except Exception:
            return HttpResponseBadRequest("Comment doesn't exist")

        template_arg = [
            "django_comments_xtd/posted.html",
            "comments/posted.html",
        ]
        return render(request, template_arg, {"target": target})
    else:
        if (
            request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
            and comment.user
            and comment.user.is_authenticated
        ):
            if comment.is_public:
                template_arg = [
                    f"django_comments_xtd/{comment.content_type.app_label}/{comment.content_type.model}/comment.html",
                    f"django_comments_xtd/{comment.content_type.app_label}/comment.html",
                    "django_comments_xtd/comment.html",
                ]
            else:
                template_arg = get_moderated_tmpl(comment)
            return render(request, template_arg, {"comment": comment})
        elif comment.is_public:
            return redirect(comment)
        else:
            moderated_tmpl = get_moderated_tmpl(comment)
            return render(request, moderated_tmpl, {"comment": comment})


def confirm(
    request, key, template_discarded="django_comments_xtd/discarded.html"
):
    try:
        tmp_comment = signed.loads(
            str(key), extra_key=settings.COMMENTS_XTD_SALT
        )
    except (ValueError, signed.BadSignature) as exc:
        return bad_request(request, exc)

    # The comment does exist if the URL was already confirmed,
    # in such a case, as per suggested in ticket #80, we return
    # the comment's URL, as if the comment is just confirmed.
    comment = _get_comment_if_exists(tmp_comment)
    if comment is not None:
        return redirect(comment)

    # Send signal that the comment confirmation has been received.
    responses = signals.confirmation_received.send(
        sender=TmpXtdComment, comment=tmp_comment, request=request
    )
    # Check whether a signal receiver decides to discard the comment.
    for __, response in responses:
        if response is False:
            return render(request, template_discarded, {"comment": tmp_comment})

    comment = _create_comment(tmp_comment)
    if comment.is_public is False:
        return render(
            request, get_moderated_tmpl(comment), {"comment": comment}
        )
    else:
        notify_comment_followers(comment)
        return redirect(comment)


def notify_comment_followers(comment):
    followers = {}
    kwargs = {
        "content_type": comment.content_type,
        "object_pk": comment.object_pk,
        "is_public": True,
        "followup": True,
    }
    previous_comments = XtdComment.objects.filter(**kwargs).exclude(
        user_email=comment.user_email
    )

    def feed_followers(gen):
        for instance in gen:
            followers[instance.user_email] = (
                instance.user_name,
                signed.dumps(
                    instance,
                    compress=True,
                    extra_key=settings.COMMENTS_XTD_SALT,
                ),
            )

    try:
        gen = previous_comments.distinct("user_email").order_by("user_email")
        feed_followers(gen)
    except NotSupportedError:
        feed_followers(previous_comments)

    subject = _("new comment posted")
    text_message_template = loader.get_template(
        "django_comments_xtd/email_followup_comment.txt"
    )
    html_message_template = loader.get_template(
        "django_comments_xtd/email_followup_comment.html"
    )

    for email, (name, key) in six.iteritems(followers):
        mute_url = reverse("comments-xtd-mute", args=[key.decode("utf-8")])
        message_context = {
            "user_name": name,
            "comment": comment,
            "content_object": comment.content_object,
            "mute_url": mute_url,
            "site": comment.site,
        }
        text_message = text_message_template.render(message_context)
        if settings.COMMENTS_XTD_SEND_HTML_EMAIL:
            html_message = html_message_template.render(message_context)
        else:
            html_message = None
        send_mail(
            subject,
            text_message,
            settings.COMMENTS_XTD_FROM_EMAIL,
            [
                email,
            ],
            html=html_message,
        )


def reply(request, cid):
    try:
        comment = XtdComment.objects.get(pk=cid)
        if not comment.allow_thread():
            raise MaxThreadLevelExceededException(comment)
    except MaxThreadLevelExceededException as exc:
        return HttpResponseForbidden(exc)
    except XtdComment.DoesNotExist as exc:
        raise Http404(exc) from exc

    options = get_app_model_options(comment)

    if not request.user.is_authenticated and options["who_can_post"] == "users":
        path = request.build_absolute_uri()
        resolved_login_url = resolve_url(settings.LOGIN_URL)
        return redirect_to_login(path, resolved_login_url, REDIRECT_FIELD_NAME)

    form = get_form()(comment.content_object, comment=comment)
    next_url = request.GET.get("next", reverse("comments-xtd-sent"))

    template_arg = [
        f"django_comments_xtd/{comment.content_type.app_label}/{comment.content_type.model}/reply.html",
        f"django_comments_xtd/{comment.content_type.app_label}/reply.html",
        "django_comments_xtd/reply.html",
    ]
    return render(
        request,
        template_arg,
        {"comment": comment, "form": form, "cid": cid, "next": next_url},
    )


def mute(request, key):
    try:
        tmp_comment = signed.loads(
            str(key), extra_key=settings.COMMENTS_XTD_SALT
        )
    except (ValueError, signed.BadSignature) as exc:
        return bad_request(request, exc)

    # Can't mute a comment that doesn't have the followup attribute
    # set to True, or a comment that doesn't exist.
    if not tmp_comment.followup or _get_comment_if_exists(tmp_comment) is None:
        raise Http404

    # Send signal that the comment thread has been muted
    signals.comment_thread_muted.send(
        sender=XtdComment, comment=tmp_comment, request=request
    )

    XtdComment.norel_objects.filter(
        content_type=tmp_comment.content_type,
        object_pk=tmp_comment.object_pk,
        user_email=tmp_comment.user_email,
        is_public=True,
        followup=True,
    ).update(followup=False)

    model = apps.get_model(
        tmp_comment.content_type.app_label, tmp_comment.content_type.model
    )
    target = model._default_manager.get(pk=tmp_comment.object_pk)

    template_arg = [
        f"django_comments_xtd/{tmp_comment.content_type.app_label}/{tmp_comment.content_type.model}/muted.html",
        f"django_comments_xtd/{tmp_comment.content_type.app_label}/muted.html",
        "django_comments_xtd/muted.html",
    ]
    return render(request, template_arg, {"content_object": target})


@csrf_protect
@login_required
def flag(request, comment_id, next_url=None, **kwargs):
    """
    Flags a comment. Confirmation on GET, action on POST.

    Templates: :template:`comments/flag.html`,
    Context:
        comment
            the flagged `comments.comment` object
    """
    next_url = next_url or kwargs.get("next")
    comment = get_object_or_404(
        get_comment_model(),
        pk=comment_id,
        site__pk=get_current_site_id(request),
    )
    if not get_app_model_options(comment=comment)["allow_flagging"]:
        ctype = ContentType.objects.get_for_model(comment.content_object)
        raise Http404(
            f"Comments posted to instances of '{ctype.app_label}"
            f".{ctype.model}' are not explicitly allowed to "
            "receive 'removal suggestion' flags. Check the "
            "COMMENTS_XTD_APP_MODEL_OPTIONS setting."
        )
    # Flag on POST
    if request.method == "POST":
        perform_flag(request, comment)
        return next_redirect(
            request, fallback=next_url or "comments-flag-done", c=comment.pk
        )

    # Render a form on GET
    else:
        return render(
            request, "comments/flag.html", {"comment": comment, "next": next}
        )


@csrf_protect
@login_required
def like(request, comment_id, next_url=None, **kwargs):
    """
    Like a comment. Confirmation on GET, action on POST.

    Templates: :template:`django_comments_xtd/like.html`,
    Context:
        comment
            the flagged `comments.comment` object
    """
    next_url = next_url or kwargs.get("next")
    comment = get_object_or_404(
        get_comment_model(),
        pk=comment_id,
        site__pk=get_current_site_id(request),
    )
    if not get_app_model_options(comment=comment)["allow_feedback"]:
        ctype = ContentType.objects.get_for_model(comment.content_object)
        raise Http404(
            f"Comments posted to instances of '{ctype.app_label}"
            f".{ctype.model}' are not explicitly allowed "
            "to receive 'liked it' flags. Check the "
            "COMMENTS_XTD_APP_MODEL_OPTIONS setting."
        )
    # Flag on POST
    if request.method == "POST":
        perform_like(request, comment)
        return next_redirect(
            request, fallback=next_url or "comments-xtd-like-done", c=comment.pk
        )
    # Render a form on GET
    else:
        flag_qs = comment.flags.prefetch_related("user").filter(
            flag=LIKEDIT_FLAG
        )
        users_likedit = [item.user for item in flag_qs]
        return render(
            request,
            "django_comments_xtd/like.html",
            {
                "comment": comment,
                "already_liked_it": request.user in users_likedit,
                "next": next_url,
            },
        )


@csrf_protect
@login_required
def dislike(request, comment_id, next_url=None, **kwargs):
    """
    Dislike a comment. Confirmation on GET, action on POST.

    Templates: :template:`django_comments_xtd/dislike.html`,
    Context:
        comment
            the flagged `comments.comment` object
    """
    next_url = next_url or kwargs.get("next")
    comment = get_object_or_404(
        get_comment_model(),
        pk=comment_id,
        site__pk=get_current_site_id(request),
    )
    if not get_app_model_options(comment=comment)["allow_feedback"]:
        ctype = ContentType.objects.get_for_model(comment.content_object)
        raise Http404(
            f"Comments posted to instances of '{ctype.app_label}"
            f".{ctype.model}' are not explicitly allowed "
            "to receive 'disliked it' flags. Check the "
            "COMMENTS_XTD_APP_MODEL_OPTIONS setting."
        )
    # Flag on POST
    if request.method == "POST":
        perform_dislike(request, comment)
        return next_redirect(
            request,
            fallback=(next_url or "comments-xtd-dislike-done"),
            c=comment.pk,
        )
    # Render a form on GET
    else:
        flag_qs = comment.flags.prefetch_related("user").filter(
            flag=DISLIKEDIT_FLAG
        )
        users_dislikedit = [item.user for item in flag_qs]
        return render(
            request,
            "django_comments_xtd/dislike.html",
            {
                "comment": comment,
                "already_disliked_it": request.user in users_dislikedit,
                "next": next_url,
            },
        )


def perform_like(request, comment):
    """Actually set the 'Likedit' flag on a comment from a request."""
    flag, created = CommentFlag.objects.get_or_create(
        comment=comment, user=request.user, flag=LIKEDIT_FLAG
    )
    if created:
        CommentFlag.objects.filter(
            comment=comment, user=request.user, flag=DISLIKEDIT_FLAG
        ).delete()
    else:
        flag.delete()
    return created


def perform_dislike(request, comment):
    """Actually set the 'Dislikedit' flag on a comment from a request."""
    flag, created = CommentFlag.objects.get_or_create(
        comment=comment, user=request.user, flag=DISLIKEDIT_FLAG
    )
    if created:
        CommentFlag.objects.filter(
            comment=comment, user=request.user, flag=LIKEDIT_FLAG
        ).delete()
    else:
        flag.delete()
    return created


like_done = confirmation_view(
    template="django_comments_xtd/liked.html",
    doc='Displays a "I liked this comment" success page.',
)

dislike_done = confirmation_view(
    template="django_comments_xtd/disliked.html",
    doc='Displays a "I disliked this comment" success page.',
)


class XtdCommentListView(ListView):
    page_range = 5
    content_types = None  # List of "app_name.model_name" strings.
    template_name = "django_comments_xtd/comment_list.html"

    def get_content_types(self):
        if self.content_types is None:
            return None
        content_types = []
        for entry in self.content_types:
            app, model = entry.split(".")
            content_types.append(
                ContentType.objects.get(app_label=app, model=model)
            )
        return content_types

    def get_queryset(self):
        content_types = self.get_content_types()
        if content_types is None:
            return None
        return (
            XtdComment.objects.for_content_types(
                content_types, site=get_current_site_id(self.request)
            )
            .filter(is_removed=False)
            .order_by("submit_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "paginator" in context:
            index = context["page_obj"].number - 1
            prange = list(context["paginator"].page_range)
            if len(prange) > self.page_range:
                if len(prange[index:]) >= self.page_range:
                    prange = prange[index : (index + self.page_range)]
                else:
                    prange = prange[-self.page_range :]
            context["page_range"] = prange
        return context
