from __future__ import unicode_literals

from django.apps import apps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.contenttypes.views import shortcut
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import F
from django.db.utils import NotSupportedError
from django.http import (
    Http404,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render, resolve_url
from django.template import loader
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.defaults import bad_request

from django_comments.signals import comment_was_posted, comment_will_be_posted
from django_comments.views.comments import CommentPostBadRequest
from django_comments.views.moderation import perform_flag
from django_comments.views.utils import next_redirect

from django_comments_xtd import (
    get_form,
    get_model as get_comment_model,
    get_reactions_enum,
    signals,
    signed,
    utils,
)
from django_comments_xtd.conf import settings
from django_comments_xtd.models import (
    CommentReaction,
    MaxThreadLevelExceededException,
    TmpXtdComment,
)


XtdComment = get_comment_model()


if len(settings.COMMENTS_XTD_THEME_DIR) > 0:
    theme_dir = f"themes/{settings.COMMENTS_XTD_THEME_DIR}"
    theme_dir_exists = utils.does_theme_dir_exist(f"comments/{theme_dir}")
else:
    theme_dir = ""
    theme_dir_exists = False


# List of possible paths to the bad_form.html template file.
if theme_dir_exists:
    _bad_form_tmpl = [
        f"comments/{theme_dir}/bad_form.html",
        "comments/bad_form.html",
    ]
else:
    _bad_form_tmpl = "comments/bad_form.html"


# List of possible paths to the preview.html template file.
_preview_tmpl = []
if theme_dir_exists:
    _preview_tmpl.extend(
        [
            "comments/{theme_dir}/{app_label}/{model}/preview.html",
            "comments/{theme_dir}/{app_label}/preview.html",
            "comments/{theme_dir}/preview.html",
        ]
    )
_preview_tmpl.extend(
    [
        "comments/{app_label}/{model}/preview.html",
        "comments/{app_label}/preview.html",
        "comments/preview.html",
    ]
)


# List of possible paths to the bad_form.html template file.
if theme_dir_exists:
    _posted_tmpl = [f"comments/{theme_dir}/posted.html", "comments/posted.html"]
else:
    _posted_tmpl = "comments/posted.html"


# List of possible paths to the moderated.html template file.
_moderated_tmpl = []
if theme_dir_exists:
    _moderated_tmpl.extend(
        [
            "comments/{theme_dir}/{app_label}/{model}/moderated.html",
            "comments/{theme_dir}/{app_label}/moderated.html",
            "comments/{theme_dir}/moderated.html",
        ]
    )
_moderated_tmpl.extend(
    [
        "comments/{app_label}/{model}/moderated.html",
        "comments/{app_label}/moderated.html",
        "comments/moderated.html",
    ]
)


# List of possible paths to the posted_js.html template file.
_posted_js_tmpl = []
if theme_dir_exists:
    _posted_js_tmpl.extend(
        [
            "comments/{theme_dir}/{app_label}/{model}/posted_js.html",
            "comments/{theme_dir}/{app_label}/posted_js.html",
            "comments/{theme_dir}/posted_js.html",
        ]
    )
_posted_js_tmpl.extend(
    [
        "comments/{app_label}/{model}/posted_js.html",
        "comments/{app_label}/posted_js.html",
        "comments/posted_js.html",
    ]
)


# List of possible paths to the published_js.html template file.
_published_js_tmpl = []
if theme_dir_exists:
    _published_js_tmpl.extend(
        [
            "comments/{theme_dir}/{app_label}/{model}/published_js.html",
            "comments/{theme_dir}/{app_label}/published_js.html",
            "comments/{theme_dir}/published_js.html",
        ]
    )
_published_js_tmpl.extend(
    [
        "comments/{app_label}/{model}/published_js.html",
        "comments/{app_label}/published_js.html",
        "comments/published_js.html",
    ]
)


# List of possible paths to the moderated_js.html template file.
_moderated_js_tmpl = []
if theme_dir_exists:
    _moderated_js_tmpl.extend(
        [
            "comments/{theme_dir}/{app_label}/{model}/moderated_js.html",
            "comments/{theme_dir}/{app_label}/moderated_js.html",
            "comments/{theme_dir}/moderated_js.html",
        ]
    )
_moderated_js_tmpl.extend(
    [
        "comments/{app_label}/{model}/moderated_js.html",
        "comments/{app_label}/moderated_js.html",
        "comments/moderated_js.html",
    ]
)


# List of possible paths to the discarded.html template file.
if theme_dir_exists:
    _discarded_tmpl = [
        f"comments/{theme_dir}/discarded.html",
        "comments/discarded.html",
    ]
else:
    _discarded_tmpl = "comments/discarded.html"


# List of possible paths to the reply.html template file.
_reply_tmpl = []
if theme_dir_exists:
    _reply_tmpl.extend(
        [
            "comments/{theme_dir}/{app_label}/{model}/reply.html",
            "comments/{theme_dir}/{app_label}/reply.html",
            "comments/{theme_dir}/reply.html",
        ]
    )
_reply_tmpl.extend(
    [
        "comments/{app_label}/{model}/reply.html",
        "comments/{app_label}/reply.html",
        "comments/reply.html",
    ]
)


# List of possible paths to the muted.html template file.
_muted_tmpl = []
if theme_dir_exists:
    _muted_tmpl.extend(
        [
            "comments/{theme_dir}/{app_label}/{model}/muted.html",
            "comments/{theme_dir}/{app_label}/muted.html",
            "comments/{theme_dir}/muted.html",
        ]
    )
_muted_tmpl.extend(
    [
        "comments/{app_label}/{model}/muted.html",
        "comments/{app_label}/muted.html",
        "comments/muted.html",
    ]
)


# List of possible paths to the react.html template file.
if theme_dir_exists:
    _react_tmpl = [f"comments/{theme_dir}/react.html", "comments/react.html"]
else:
    _react_tmpl = "comments/react.html"


# List of possible paths to the reacted.html template file.
if theme_dir_exists:
    _reacted_tmpl = [
        f"comments/{theme_dir}/reacted.html",
        "comments/reacted.html",
    ]
else:
    _reacted_tmpl = "comments/reacted.html"


@csrf_protect
@require_POST
def post(request, next=None, using=None):
    """
    Post a comment.

    HTTP POST is required. If ``POST['submit'] == "preview"`` or if there are
    errors a preview template, ``comments/<theme_dir>/preview.html``, will be
    rendered.

    This function is copied from the original in django-comments. It extends
    it to check whether the comment form has a field with the name indicated in
    the setting COMMENTS_XTD_PAGE_QUERY_STRING_PARAM. If so it is added to the
    context passed to the template as `page_number`, which corresponds to the
    comment's page number in which the comment has been displayed.
    """
    if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        return post_js(request, next, using)

    data = request.POST.copy()
    if request.user.is_authenticated:
        if not data.get("name", ""):
            data["name"] = (
                request.user.get_full_name() or request.user.get_username()
            )
        if not data.get("email", ""):
            data["email"] = request.user.email

    # Look up the object we're trying to comment about.
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = apps.get_model(*ctype.split(".", 1))
        target = model._default_manager.using(using).get(pk=object_pk)
    except (LookupError, TypeError):
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype)
        )
    except AttributeError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model."
            % escape(ctype)
        )
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists."
            % (escape(ctype), escape(object_pk))
        )
    except (ValueError, ValidationError) as e:
        return CommentPostBadRequest(
            "Attempting to get content-type %r and object PK %r raised %s"
            % (escape(ctype), escape(object_pk), e.__class__.__name__)
        )

    # Do we want to preview the comment?
    preview = "preview" in data

    # Construct the comment form
    form = get_form()(target, data=data)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s"
            % escape(str(form.security_errors()))
        )

    cpage_qs_param = settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM
    cpage = request.POST.get(cpage_qs_param, None)

    # If there are errors or if we requested a preview show the comment.
    if form.errors or preview:
        template_list = [
            pth.format(
                theme_dir=theme_dir,
                app_label=model._meta.app_label,
                model=model._meta.model_name,
            )
            for pth in _preview_tmpl
        ]
        print(template_list)
        return render(
            request,
            template_list,
            {
                "comment": form.data.get("comment", ""),
                "form": form,
                "is_reply": bool(form.data.get("reply_to")),
                "next": data.get("next", next),
                "page_number": cpage,
                "cpage_qs_param": cpage_qs_param,
                "dcx_theme_dir": theme_dir,
            },
        )

    # Otherwise create the comment
    comment = form.get_comment_object(site_id=get_current_site(request).id)
    comment.ip_address = request.META.get("REMOTE_ADDR", None) or None
    comment.page_number = cpage
    if request.user.is_authenticated:
        comment.user = request.user

    # Signal that the comment is about to be saved
    responses = comment_will_be_posted.send(
        sender=comment.__class__, comment=comment, request=request
    )

    for (receiver, response) in responses:
        if response is False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment"
                % receiver.__name__
            )

    # Save the comment and signal that it was saved
    comment.save()
    comment_was_posted.send(
        sender=comment.__class__, comment=comment, request=request
    )

    kwargs = {
        "c": comment._get_pk_val(),
    }
    if cpage is not None:
        kwargs[settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM] = cpage

    return next_redirect(
        request, fallback=next or "comments-comment-done", **kwargs
    )


def json_res(request, template_search_list, context, status=200):
    html = loader.render_to_string(template_search_list, context, request)
    json_context = {"html": html, "reply_to": request.POST.get("reply_to", "0")}
    if "field_focus" in context:
        json_context.update({"field_focus": context["field_focus"]})
    return JsonResponse(json_context, status=status)


def post_js(request, next=None, using=None):
    """
    Handles a comment post when the request is an XMLHttpRequest.
    """
    data = request.POST.copy()
    if request.user.is_authenticated:
        if not data.get("name", ""):
            data["name"] = (
                request.user.get_full_name() or request.user.get_username()
            )
        if not data.get("email", ""):
            data["email"] = request.user.email

    # Look up the object we're trying to comment about.
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        context = {"bad_error": "Missing content_type or object_pk field."}
        return json_res(request, _bad_form_tmpl, context, status=400)

    try:
        model = apps.get_model(*ctype.split(".", 1))
        target = model._default_manager.using(using).get(pk=object_pk)
    except (LookupError, TypeError):
        error_msg = "Invalid content_type value: %r" % escape(ctype)
        context = {"bad_error": error_msg}
        return json_res(request, _bad_form_tmpl, context, status=400)
    except AttributeError:
        error_msg = (
            "The given content-type %r does not resolve to a valid model."
            % escape(ctype)
        )
        context = {"bad_error": error_msg}
        return json_res(request, _bad_form_tmpl, context, status=400)
    except ObjectDoesNotExist:
        error_msg = (
            "No object matching content-type %r and object PK %r exists."
            % (
                escape(ctype),
                escape(object_pk),
            )
        )
        context = {"bad_error": error_msg}
        return json_res(request, _bad_form_tmpl, context, status=400)
    except (ValueError, ValidationError) as e:
        error_msg = (
            "Attempting to get content-type %r and object PK %r raised %s"
            % (
                escape(ctype),
                escape(object_pk),
                e.__class__.__name__,
            )
        )
        context = {"bad_error": error_msg}
        return json_res(request, _bad_form_tmpl, context, status=400)

    # Do we want to preview the comment?
    preview = "preview" in data

    # Construct the comment form
    form = get_form()(target, data=data)

    # Check security information
    if form.security_errors():
        error_msg = "The comment form failed security verification."
        context = {"bad_error": error_msg}
        return json_res(request, _bad_form_tmpl, context, status=400)

    cpage_qs_param = settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM
    cpage = request.POST.get(cpage_qs_param, None)

    # If there are errors or if we requested a preview show the comment.
    if form.errors or preview:
        # Use different template depending on whether it's a reply or not.
        if form.data.get("reply_to", "0") != "0":
            template_name = "reply_form_js.html"
        else:
            template_name = "form_js.html"

        template_list = [
            f"comments/{theme_dir}/%s/%s/{template_name}"
            % (model._meta.app_label, model._meta.model_name),
            f"comments/{theme_dir}/%s/{template_name}" % model._meta.app_label,
            f"comments/{theme_dir}/{template_name}",
            f"comments/{template_name}",
        ]
        if form.errors:
            field_focus = [key for key in form.errors.keys()][0]
        else:
            field_focus = None

        context = {
            "display_preview": not form.errors,
            "comment": form.data.get("comment", ""),
            "form": form,
            "field_focus": field_focus,
            "is_reply": form.data.get("reply_to", "0") != "0",
            "next": data.get("next", next),
            "page_number": cpage,
            "cpage_qs_param": cpage_qs_param,
        }
        return json_res(request, template_list, context, status=200)

    # Otherwise create the comment
    comment = form.get_comment_object(site_id=get_current_site(request).id)
    comment.ip_address = request.META.get("REMOTE_ADDR", None) or None
    comment.page_number = cpage
    if request.user.is_authenticated:
        comment.user = request.user

    # Signal that the comment is about to be saved
    responses = comment_will_be_posted.send(
        sender=comment.__class__, comment=comment, request=request
    )

    for (receiver, response) in responses:
        if response is False:
            if settings.DEBUG:
                error_msg = (
                    "comment_will_be_posted receiver %r killed the comment"
                    % receiver.__name__
                )
            else:
                error_msg = "Your comment has been rejected."

            context = {"bad_error": error_msg}
            return render(request, _bad_form_tmpl, context, status=400)

    # Save the comment and signal that it was saved
    comment.save()
    comment_was_posted.send(
        sender=comment.__class__, comment=comment, request=request
    )
    return sent_js(request, comment, using=using)


def send_email_confirmation_request(
    comment,
    key,
    site,
    text_template="comments/email_confirmation_request.txt",
    html_template="comments/email_confirmation_request.html",
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

    utils.send_mail(
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
    tmp_comment.pop("page_number", None)
    comment = XtdComment(**tmp_comment)
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

    ct = comment.get("content_type")
    ct_str = "%s.%s" % (ct.app_label, ct.model)
    options = utils.get_app_model_options(content_type=ct_str)
    if not user_is_authenticated and options["who_can_post"] == "users":
        # Reject comment.
        return False
    else:
        return True


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

        return render(request, _posted_tmpl, {"target": target})
    else:
        if comment.is_public:
            return utils.redirect_to(comment, request=request)
        else:
            template_list = [
                pth.format(
                    theme_dir=theme_dir,
                    app_label=comment.content_type.app_label,
                    model=comment.content_type.model,
                )
                for pth in _moderated_tmpl
            ]
            return render(request, template_list, {"comment": comment})


def sent_js(request, comment, using=None):

    try:
        comment_pk = comment._get_pk_val()
        comment = XtdComment.objects.get(pk=comment_pk)
    except (TypeError, ValueError, XtdComment.DoesNotExist):
        try:
            value = signing.loads(comment_pk)
            ctype, object_pk = value.split(":")
            model = apps.get_model(*ctype.split(".", 1))
            target = model._default_manager.using(using).get(pk=object_pk)
        except Exception:
            context = {"bad_error": "Comment does not exist."}
            return json_res(request, _bad_form_tmpl, context, status=400)
        app_label, model_name = ctype.split(".", 1)
        template_list = [
            pth.format(
                theme_dir=theme_dir, app_label=app_label, model=model_name
            )
            for pth in _posted_js_tmpl
        ]
        return json_res(request, template_list, {"target": target}, status=202)
    else:
        if comment.is_public:
            # Return a render instead of a redirect_to. But use status=201.
            # In comment_form.js check whether the status is 201 to read
            # the content as the redirect_url.
            template_list = [
                pth.format(
                    theme_dir=theme_dir,
                    app_label=comment.content_type.app_label,
                    model=comment.content_type.model,
                )
                for pth in _published_js_tmpl
            ]
            page_number = utils.get_comment_page_number(
                request, comment.content_type.id, comment.object_pk, comment.id
            )
            comment_url = utils.get_comment_url(comment, None, page_number)
            return json_res(
                request,
                template_list,
                {"comment": comment, "comment_url": comment_url},
                status=201,
            )
        else:
            template_list = [
                pth.format(
                    theme_dir=theme_dir,
                    app_label=comment.content_type.app_label,
                    model=comment.content_type.model,
                )
                for pth in _moderated_js_tmpl
            ]
            return json_res(
                request, template_list, {"comment": comment}, status=201
            )


def confirm(request, key, template_discarded=_discarded_tmpl):
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
    page_number = tmp_comment.pop("page_number", None)

    if comment is not None:
        return utils.redirect_to(comment, page_number=page_number)

    # Send signal that the comment confirmation has been received.
    responses = signals.confirmation_received.send(
        sender=TmpXtdComment, comment=tmp_comment, request=request
    )
    # Check whether a signal receiver decides to discard the comment.
    for (receiver, response) in responses:
        if response is False:
            return render(request, template_discarded, {"comment": tmp_comment})

    comment = _create_comment(tmp_comment)
    if comment.is_public is False:
        template_list = [
            pth.format(
                theme_dir=theme_dir,
                app_label=comment.content_type.app_label,
                model=comment.content_type.model,
            )
            for pth in _moderated_tmpl
        ]
        return render(request, template_list, {"comment": comment})
    else:
        notify_comment_followers(comment)
        return utils.redirect_to(comment, page_number=page_number)


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

    for instance in previous_comments:
        followers[instance.user_email] = (
            instance.user_name,
            signed.dumps(
                instance, compress=True, extra_key=settings.COMMENTS_XTD_SALT
            ),
        )

    subject = _("new comment posted")
    text_message_template = loader.get_template(
        "comments/email_followup_comment.txt"
    )
    if settings.COMMENTS_XTD_SEND_HTML_EMAIL:
        html_message_template = loader.get_template(
            "comments/email_followup_comment.html"
        )

    for email, (name, key) in followers.items():
        mute_url = reverse("comments-xtd-mute", args=[key.decode("utf-8")])
        message_context = {
            "user_name": name,
            "comment": comment,
            # 'content_object': target,
            "mute_url": mute_url,
            "site": comment.site,
        }
        text_message = text_message_template.render(message_context)
        if settings.COMMENTS_XTD_SEND_HTML_EMAIL:
            html_message = html_message_template.render(message_context)
        else:
            html_message = None
        utils.send_mail(
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
        raise Http404(exc)

    ct_str = "%s.%s" % (
        comment.content_type.app_label,
        comment.content_type.model,
    )
    options = utils.get_app_model_options(content_type=ct_str)

    if not request.user.is_authenticated and options["who_can_post"] == "users":
        path = request.build_absolute_uri()
        resolved_login_url = resolve_url(settings.LOGIN_URL)
        return redirect_to_login(path, resolved_login_url, REDIRECT_FIELD_NAME)

    form = get_form()(comment.content_object, comment=comment)
    next = request.GET.get("next", reverse("comments-xtd-sent"))

    cpage_qs_param = settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM
    cpage = request.POST.get(cpage_qs_param, None)

    template_list = [
        pth.format(
            theme_dir=theme_dir,
            app_label=comment.content_type.app_label,
            model=comment.content_type.model,
        )
        for pth in _reply_tmpl
    ]
    return render(
        request,
        template_list,
        {
            "comment": comment,
            "form": form,
            "cid": cid,
            "next": next,
            "page_number": cpage,
            "cpage_qs_param": cpage_qs_param,
        },
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
    template_list = [
        pth.format(
            theme_dir=theme_dir,
            app_label=tmp_comment.content_type.app_label,
            model=tmp_comment.content_type.model,
        )
        for pth in _muted_tmpl
    ]
    return render(request, template_list, {"content_object": target})


@csrf_protect
@login_required
def flag(request, comment_id, next=None):
    """
    Flags a comment. Confirmation on GET, action on POST.

    Templates: :template:`comments/flag.html`,
    Context:
        comment_id
            The id of the comment the user is flagging.
    """
    comment = get_object_or_404(
        get_comment_model(),
        pk=comment_id,
        site__pk=utils.get_current_site_id(request),
    )
    utils.check_option(comment, "comment_flagging_enabled")

    # Flag on POST.
    if request.method == "POST":
        perform_flag(request, comment)
        return next_redirect(
            request, fallback=next or "comments-flag-done", c=comment.pk
        )

    # Render a form on GET
    else:
        return render(
            request,
            "comments/flag.html",
            {
                "comment": comment,
                "next": next,
            },
        )


@csrf_protect
@login_required
def react(request, comment_id, next=None):
    """
    A registered user reacts to a comment. Confirmation on GET, action on POST.

    Templates: :template:`comments/<theme_dir>/react.html`,
    Context:
        comment
            the `comments.comment` object the user reacted to.
    """
    comment = get_object_or_404(
        get_comment_model(),
        pk=comment_id,
        site__pk=utils.get_current_site_id(request),
    )
    utils.check_option(comment, "comment_reactions_enabled")

    cpage_qs_param = settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM
    cpage = request.GET.get(cpage_qs_param, None)

    if request.method == "POST":
        created = perform_react(request, comment)

        # When the reaction has been sent via JavaScript.
        if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
            obj_meta = comment.content_object._meta
            template_name = "comment_reactions.html"
            template_list = [
                f"comments/{theme_dir}/%s/%s/{template_name}"
                % (obj_meta.app_label, obj_meta.model_name),
                f"comments/{theme_dir}/%s/{template_name}" % obj_meta.app_label,
                f"comments/{theme_dir}/{template_name}",
                f"comments/{template_name}",
            ]
            context = {"comment": comment}
            status = 201 if created else 200
            return json_res(request, template_list, context, status=status)

        kwargs = {
            "c": comment.pk,
            cpage_qs_param: cpage or request.POST.get(cpage_qs_param, None),
        }
        return next_redirect(
            request, fallback=next or "comments-xtd-react-done", **kwargs
        )
    else:
        user_reactions = []
        cr_qs = CommentReaction.objects.filter(
            comment=comment, authors=request.user
        )
        for cmt_reaction in cr_qs:
            user_reactions.append(get_reactions_enum()(cmt_reaction.reaction))

        return render(
            request,
            _react_tmpl,
            {
                "comment": comment,
                "user_reactions": user_reactions,
                "next": next,
                "page_number": cpage,
                "cpage_qs_param": cpage_qs_param,
                "dcx_theme_dir": theme_dir,
            },
        )


def perform_react(request, comment):
    """Save the user reaction and send the signal comment_got_a_reaction."""
    created = False
    cr_qs = CommentReaction.objects.filter(
        reaction=request.POST["reaction"], comment=comment
    )
    if cr_qs.filter(authors=request.user).count() == 1:
        if cr_qs[0].counter == 1:
            cr_qs.delete()
        else:
            cr_qs.update(counter=F("counter") - 1)
            cr_qs[0].authors.remove(request.user)
    else:
        cmt_reaction, created = CommentReaction.objects.get_or_create(
            reaction=request.POST["reaction"], comment=comment
        )
        cmt_reaction.authors.add(request.user)
        cmt_reaction.counter += 1
        cmt_reaction.save()
    signals.comment_got_a_reaction.send(
        sender=comment.__class__,
        comment=comment,
        reaction=request.POST["reaction"],
        created=created,
        request=request,
    )
    return created


def react_done(request):
    """Displays a "User reacted to this comment" success page."""
    comment_pk = request.GET.get("c", None)
    cpage_qs_param = settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM
    cpage = request.GET.get(cpage_qs_param, 1)
    if comment_pk:
        comment = get_object_or_404(
            get_comment_model(),
            pk=comment_pk,
            site__pk=utils.get_current_site_id(request),
        )
    else:
        comment = None
    return render(
        request,
        _reacted_tmpl,
        {
            "comment": comment,
            "page_number": int(cpage),
            "dcx_theme_dir": theme_dir,
        },
    )


def comment_in_page(request, content_type_id, object_id, comment_id):
    response = shortcut(request, content_type_id, object_id)
    qs_param = settings.COMMENTS_XTD_PAGE_QUERY_STRING_PARAM
    page = request and request.GET.get(qs_param, None) or None
    if not page:
        # Create a CommentsPaginator and get the page of the comment.
        page = utils.get_comment_page_number(
            request, content_type_id, object_id, comment_id
        )

    try:
        page_number = int(page)
    except ValueError:
        if page == "last":
            return HttpResponseRedirect(f"{response.url}?{qs_param}={page}")
        else:
            raise Http404(
                _("Page is not “last”, nor can it " "be converted to an int.")
            )
    if page_number > 1:
        return HttpResponseRedirect(f"{response.url}?{qs_param}={page}")
    else:
        return HttpResponseRedirect(response.url)
