from typing import ClassVar
from urllib.parse import urlencode

from django import http
from django.apps import apps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.contenttypes.views import shortcut
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.core.exceptions import (
    ImproperlyConfigured,
    ObjectDoesNotExist,
    ValidationError,
)
from django.db import transaction
from django.db.models import F
from django.db.utils import NotSupportedError
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.template import loader
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.defaults import bad_request
from django.views.generic import DetailView, ListView, RedirectView
from django.views.generic.edit import FormView
from django_comments import signals as djc_signals
from django_comments.models import CommentFlag
from django_comments.views.comments import CommentPostBadRequest

from django_comments_xtd import (
    get_form,
    get_model,
    get_reaction_enum,
    signed,
    utils,
)
from django_comments_xtd import signals as djcx_signals
from django_comments_xtd.conf import settings
from django_comments_xtd.models import (
    CommentReaction,
    CommentVote,
    MaxThreadLevelExceededException,
    TmpXtdComment,
)
from django_comments_xtd.templating import get_template_list

XtdComment = get_model()


# ---------------------------------------------------------------------
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


def get_comment_if_exists(comment: TmpXtdComment):
    """
    Returns either an XtdComment matching the TmpXtdComment, or None.

    The attributes that have to match between the TmpXtdComment and the
    XtdComment are 'user_name', 'user_email' and 'submit_date'.

    """
    return XtdComment.objects.filter(
        user_name=comment.user_name,
        user_email=comment.user_email,
        followup=comment.followup,
        submit_date=comment.submit_date,
    ).first()


def create_comment(tmp_comment):
    """
    Creates an XtdComment from a TmpXtdComment.
    """
    comment = XtdComment(**tmp_comment)
    if settings.COMMENTS_XTD_FOR_CONCRETE_MODEL is False:
        comment.content_type = tmp_comment["content_type"]
    comment.save()
    return comment


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
            "content_object": comment.content_object,
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


def confirm(request, key, template_discarded=None, template_moderated=None):
    try:
        tmp_comment = signed.loads(
            str(key), extra_key=settings.COMMENTS_XTD_SALT
        )
    except (ValueError, signed.BadSignature) as exc:
        return bad_request(request, exc)

    # The comment does exist if the URL was already confirmed,
    # in such a case, as per suggested in ticket #80, we return
    # the comment's URL, as if the comment is just confirmed.
    comment = get_comment_if_exists(tmp_comment)
    if comment is not None:
        return redirect(comment)

    # Send signal that the comment confirmation has been received.
    responses = djcx_signals.confirmation_received.send(
        sender=TmpXtdComment, comment=tmp_comment, request=request
    )
    # Check whether a signal receiver decides to discard the comment.
    for __, response in responses:
        if response is False:
            if template_discarded is None:
                template_discarded = get_template_list("discarded")
            return render(request, template_discarded, {"comment": tmp_comment})

    comment = create_comment(tmp_comment)
    if comment.is_public is False:
        if template_moderated is None:
            template_list = get_template_list(
                "moderated",
                app_label=comment.content_type.app_label,
                model=comment.content_type.model,
            )
        else:
            template_list = template_moderated
        return render(request, template_list, {"comment": comment})
    else:
        notify_comment_followers(comment)
        return redirect(comment)


def sent(request, using=None, template_posted=None, template_moderated=None):
    comment_pk = request.GET.get("c", None)
    if not comment_pk:
        return CommentPostBadRequest("Comment doesn't exist")
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
            return CommentPostBadRequest("Comment doesn't exist")
        if template_posted is None:
            template_posted = get_template_list("posted")
        return render(request, template_posted, {"target": target})
    else:
        if comment.is_public:
            return redirect(comment)
        else:
            if template_moderated is None:
                template_moderated = get_template_list(
                    "moderated",
                    app_label=comment.content_type.app_label,
                    model=comment.content_type.model,
                )
            return render(request, template_moderated, {"comment": comment})


# ---------------------------------------------------------------------
def on_comment_will_be_posted(sender, comment, request, **kwargs):
    """
    Check whether there are conditions to reject the post.

    Returns False if there are conditions to reject the comment.
    """
    if settings.COMMENTS_APP != "django_comments_xtd":  # pragma: no cover
        # Do not kill the post if handled by other commenting app.
        return True

    if comment.user:
        user_is_authenticated = comment.user.is_authenticated
    else:
        user_is_authenticated = False

    options = utils.get_app_model_options(comment)
    return not (  # Return False to reject comment.
        options["who_can_post"] == "users" and not user_is_authenticated
    )


djc_signals.comment_will_be_posted.connect(
    on_comment_will_be_posted, sender=TmpXtdComment
)


# ---------------------------------------------------------------------
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
        if get_comment_if_exists(comment) is None:
            new_comment = create_comment(comment)
            comment.xtd_comment = new_comment
            djcx_signals.confirmation_received.send(
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


djc_signals.comment_was_posted.connect(
    on_comment_was_posted, sender=TmpXtdComment
)


# ---------------------------------------------------------------------
class CommentUrlView(RedirectView):
    def get_redirect_url(self, content_type_id, object_id, comment_id):
        self.request.session["djcx_highlight_cid"] = int(comment_id)
        response = shortcut(self.request, content_type_id, object_id)
        return response.url


class BadRequestError(Exception):
    """Exception raised for a bad post request."""

    def __init__(self, why):
        self.why = why


class CommentsParamsMixin:
    """A mixin for views to get django-comments-xtd query string parameters."""

    def get_next_redirect_url(self, fallback, **kwargs):
        next = self.request.POST.get("next")

        if not url_has_allowed_host_and_scheme(
            url=next, allowed_hosts={self.request.get_host()}
        ):
            next = resolve_url(fallback)

        if kwargs:
            if "#" in next:
                tmp = next.rsplit("#", 1)
                next = tmp[0]
                anchor = "#" + tmp[1]
            else:
                anchor = ""

            joiner = (("?" in next) and "&") or "?"
            next += joiner + urlencode(kwargs) + anchor

        return next


class JsonResponseMixin:
    def json_response(self, template_list, context, status):
        html = loader.render_to_string(template_list, context, self.request)
        json_context = {
            "html": html.strip(),
            "reply_to": self.request.POST.get("reply_to", "0"),
        }
        if "field_focus" in context:
            json_context.update({"field_focus": context["field_focus"]})
        return http.JsonResponse(json_context, status=status)


class SingleTmpCommentView(DetailView):
    http_method_names: ClassVar = [
        "get",
    ]
    context_object_name = "comment"
    template_alias = None

    def get_object(self, key):
        return signed.loads(str(key), extra_key=settings.COMMENTS_XTD_SALT)

    def get_template_names(self):
        if self.template_alias is None:
            raise ImproperlyConfigured(
                "SingleTmpCommentView requires either a definition of "
                "'template_alias' or an implementation of "
                "'get_template_names()'"
            )
        return get_template_list(
            self.template_alias,
            app_label=self.object.content_type.app_label,
            model=self.object.content_type.model,
        )


class SingleCommentView(CommentsParamsMixin, JsonResponseMixin, DetailView):
    context_object_name = "comment"
    model = get_model()
    check_option = None
    is_ajax = False

    # Possible values for template_alias and template_alias_js come from
    # the keys of the dictionary _template_pattern_paths, in the
    # module `django_comments_xtd.views.templates`.
    template_alias = None
    template_alias_js = None

    def get_object(self, comment_id):
        comment = get_object_or_404(
            self.model,
            pk=comment_id,
            site__pk=utils.get_current_site_id(self.request),
        )
        self.options = utils.get_app_model_options(
            content_type=comment.content_type
        )

        if self.check_option is not None:
            utils.check_option(self.check_option, options=self.options)

        check_input_allowed_str = self.options.pop("check_input_allowed")
        check_func = import_string(check_input_allowed_str)
        target_obj = comment.content_type.get_object_for_this_type(
            pk=comment.object_pk
        )
        self.is_input_allowed = check_func(target_obj)

        if not self.is_input_allowed:
            raise http.Http404(_("Input is not allowed."))

        return comment

    def get_template_names(self):
        template_alias = (
            self.template_alias_js if self.is_ajax else self.template_alias
        )
        if template_alias is None:
            raise ImproperlyConfigured(
                "SingleCommentView requires either a definition of "
                "'template_alias' or an implementation of "
                "'get_template_names()'"
            )

        return get_template_list(
            template_alias,
            app_label=self.object.content_object._meta.app_label,
            model=self.object.content_object._meta.model_name,
        )

    def get_context_data(self, **kwargs):
        kwargs.update(self.options)
        return super().get_context_data(
            comments_input_allowed=self.is_input_allowed,
            **kwargs,
        )


@method_decorator(csrf_protect, name="dispatch")
class PostCommentView(CommentsParamsMixin, JsonResponseMixin, FormView):
    context_object_name = "comment"
    http_method_names: ClassVar = [
        "post",
    ]
    is_ajax = False

    # Templates when returning from an Ajax request.
    moderated_js_template_alias = "moderated_js"

    def get_target_object(self, data):
        ctype = data.get("content_type")
        object_pk = data.get("object_pk")
        if ctype is None or object_pk is None:
            raise BadRequestError("Missing content_type or object_pk field.")

        self.using = self.kwargs.get("using")
        try:
            model = apps.get_model(*ctype.split(".", 1))
            return model._default_manager.using(self.using).get(pk=object_pk)
        except (LookupError, TypeError) as exc:
            raise BadRequestError(
                f"Invalid content_type value: {escape(ctype)!r}"
            ) from exc
        except AttributeError as exc:
            raise BadRequestError(
                f"The given content-type {escape(ctype)!r} does not "
                "resolve to a valid model."
            ) from exc
        except ObjectDoesNotExist as exc:
            raise BadRequestError(
                f"No object matching content-type {escape(ctype)!r} and "
                f"object PK {object_pk!r} exists."
            ) from exc
        except (ValueError, ValidationError) as exc:
            raise BadRequestError(
                f"Attempting to get content-type {escape(ctype)!r} "
                f"and object PK {escape(object_pk)!r} "
                f"raised {exc.__class__.__name__}"
            ) from exc

    def get_form_kwargs(self):
        data = self.request.POST.copy()
        if self.request.user.is_authenticated:
            if not data.get("name", ""):
                data["name"] = (
                    self.request.user.get_full_name()
                    or self.request.user.get_username()
                )
            if not data.get("email", ""):
                data["email"] = self.request.user.email
        return data

    def get_form_class(self):
        return get_form()

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.target_object, data=self.data)

    def _create_comment(self, form):
        comment = form.get_comment_object(
            site_id=get_current_site(self.request).id
        )
        comment.ip_address = self.request.META.get("REMOTE_ADDR", None) or None
        if self.request.user.is_authenticated:
            comment.user = self.request.user

        # Signal that the comment is about to be saved.
        responses = djc_signals.comment_will_be_posted.send(
            sender=comment.__class__, comment=comment, request=self.request
        )

        for receiver, response in responses:
            if response is False:
                msg = (
                    f"comment_will_be_posted receiver {receiver.__name__!r} "
                    "killed the comment"
                )
                raise BadRequestError(msg)

        # Save the comment and signal that it was saved
        comment.save()
        djc_signals.comment_was_posted.send(
            sender=comment.__class__, comment=comment, request=self.request
        )
        return comment

    def get_template_names(self):
        return get_template_list(
            "preview",
            app_label=self.target_object._meta.app_label,
            model=self.target_object._meta.model_name,
        )

    def get_success_url(self):
        return self.get_next_redirect_url(
            "comments-comment-done", c=self.object._get_pk_val()
        )

    def get_context_data(self, **kwargs):
        if "form" in kwargs:
            form = kwargs.get("form")
            kwargs.update(
                {
                    "is_reply": form.data.get("reply_to", "0") != "0",
                    "next": self.data.get("next", None),
                }
            )
            if self.is_ajax:
                if form.errors:
                    field_focus = next(iter(form.errors.keys()))
                else:
                    field_focus = None
                kwargs.update(
                    {
                        "display_preview": not form.errors,
                        "field_focus": field_focus,
                    }
                )
        return super().get_context_data(**kwargs)

    def comment_posted(self):
        try:
            value = signing.loads(self.object._get_pk_val())
            ctype, object_pk = value.split(":")
            model = apps.get_model(*ctype.split(".", 1))
            target = model._default_manager.using(self.using).get(pk=object_pk)
        except Exception:
            context = {"error_msg": "Comment does not exist."}
            bad_form_templates = get_template_list("bad_form")
            return self.json_response(bad_form_templates, context, status=400)

        app_label, model_name = ctype.split(".", 1)
        templates = get_template_list(
            "posted_js", app_label=app_label, model=model_name
        )
        return self.json_response(templates, {"target": target}, status=202)

    def comment_published(self):
        templates = get_template_list(
            "published_js",
            app_label=self.target_object._meta.app_label,
            model=self.target_object._meta.model_name,
        )
        comment_url = self.object.get_absolute_url()
        return self.json_response(
            templates,
            {"comment": self.object, "comment_url": comment_url},
            status=201,
        )

    def comment_moderated(self):
        templates = get_template_list(
            "moderated_js",
            app_label=self.target_object._meta.app_label,
            model=self.target_object._meta.model_name,
        )
        return self.json_response(
            templates, {"comment": self.object}, status=201
        )

    def post_js_response(self):
        try:
            self.object = XtdComment.objects.get(pk=self.object._get_pk_val())
        except (TypeError, ValueError, XtdComment.DoesNotExist):
            return self.comment_posted()
        else:
            if self.object.is_public:
                return self.comment_published()
            else:
                return self.comment_moderated()

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        if self.is_ajax:
            if self.data.get("reply_to") != "0":
                templates = get_template_list(
                    "reply_form_js",
                    app_label=self.target_object._meta.app_label,
                    model=self.target_object._meta.model_name,
                )
            else:
                templates = get_template_list(
                    "form_js",
                    app_label=self.target_object._meta.app_label,
                    model=self.target_object._meta.model_name,
                )
            return self.json_response(templates, context, status=200)
        else:
            return self.render_to_response(context)

    def _handle_std_post(self):
        try:
            self.target_object = self.get_target_object(self.data)
        except BadRequestError as exc:
            return CommentPostBadRequest(exc.why)

        form = self.get_form()

        if form.security_errors():
            return CommentPostBadRequest(
                "The comment form failed security verification: "
                f"{escape(str(form.security_errors()))}"
            )
        if not form.is_valid() or "preview" in self.data:
            return self.form_invalid(form)
        try:
            self.object = self._create_comment(form)
        except BadRequestError as exc:
            return CommentPostBadRequest(exc.why)
        else:
            return self.form_valid(form)

    def _handle_ajax_post(self):
        try:
            self.target_object = self.get_target_object(self.data)
        except BadRequestError as exc:
            context = {"error_msg": exc.why}
            templates = get_template_list("bad_form")
            return self.json_response(templates, context, status=400)

        form = self.get_form()

        if form.security_errors():
            error_msg = "The comment form failed security verification."
            context = {"error_msg": error_msg}
            templates = get_template_list("bad_form")
            return self.json_response(templates, context, status=400)

        if not form.is_valid() or "preview" in self.data:
            return self.form_invalid(form)

        try:
            self.object = self._create_comment(form)
        except BadRequestError as exc:
            if not settings.DEBUG:  # pragma: no cover
                msg = "Your comment has been rejected."
            else:
                msg = exc.why
            templates = get_template_list("bad_form")
            return self.json_response(templates, {"error_msg": msg}, status=400)
        else:
            return self.post_js_response()

    def post(self, request):
        self.object = None
        self.target_object = None
        self.data = self.get_form_kwargs()

        if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
            self.is_ajax = True
            return self._handle_ajax_post()
        return self._handle_std_post()


class ReplyCommentView(SingleCommentView):
    http_method_names: ClassVar = [
        "get",
    ]
    template_alias = "reply"

    def get(self, request, cid):
        self.object = self.get_object(cid)

        if not self.object.allow_thread():
            return http.HttpResponseForbidden(
                MaxThreadLevelExceededException(self.object)
            )

        if (
            not self.request.user.is_authenticated
            and self.options["who_can_post"] == "users"
        ):
            path = request.build_absolute_uri()
            login_url = resolve_url(settings.LOGIN_URL)
            return redirect_to_login(path, login_url, REDIRECT_FIELD_NAME)

        form = get_form()(self.object.content_object, comment=self.object)
        next = request.GET.get("next", reverse("comments-xtd-sent"))
        context = self.get_context_data(form=form, next=next)
        return self.render_to_response(context)


class MuteCommentView(SingleTmpCommentView):
    """Implements the GET request to disable notifications on new comments."""

    template_alias = "muted"

    def get_object(self, key):
        tmp_comment = super().get_object(key)

        # Can't mute a comment that doesn't have the followup attribute
        # set to True, or a comment that doesn't exist.
        if (
            not tmp_comment.followup
            or get_comment_if_exists(tmp_comment) is None
        ):
            raise http.Http404(
                _("Comment already muted or comment does not exist.")
            )

        return tmp_comment

    def perform_mute(self):
        XtdComment.norel_objects.filter(
            content_type=self.object.content_type,
            object_pk=self.object.object_pk,
            user_email=self.object.user_email,
            is_public=True,
            followup=True,
        ).update(followup=False)

        # Send signal that the comment thread has been muted
        djcx_signals.comment_thread_muted.send(
            sender=XtdComment, comment=self.object, request=self.request
        )

    def get(self, request, key):
        try:
            self.object = self.get_object(key)
        except (ValueError, signed.BadSignature) as exc:
            return bad_request(request, exc)
        # model = apps.get_model(
        #     self.object.content_type.app_label, self.object.content_type.model
        # )
        # target = model._default_manager.get(pk=self.object.object_pk)
        self.perform_mute()
        context = self.get_context_data()  # (content_object=target)
        return self.render_to_response(context)


@method_decorator([csrf_protect, login_required], name="dispatch")
class FlagCommentView(SingleCommentView):
    check_option = "comments_flagging_enabled"
    template_alias = "flag"
    template_alias_js = "flag_js"
    context_object_name = "comment"

    def perform_flag(self):
        created = False

        flag_qs = CommentFlag.objects.filter(
            comment=self.object,
            user=self.request.user,
            flag=CommentFlag.SUGGEST_REMOVAL,
        )

        if flag_qs.count() == 1:
            flag_qs.delete()
            flag = None
        else:
            flag, created = CommentFlag.objects.get_or_create(
                comment=self.object,
                user=self.request.user,
                flag=CommentFlag.SUGGEST_REMOVAL,
            )

        djc_signals.comment_was_flagged.send(
            sender=self.object.__class__,
            comment=self.object,
            flag=flag,
            created=created,
            request=self.request,
        )

    def get(self, request, comment_id, next=None):
        self.object = self.get_object(comment_id)
        context = self.get_context_data(object=self.object, next=next)
        user_flag_qs = CommentFlag.objects.filter(
            flag=CommentFlag.SUGGEST_REMOVAL,
            comment=self.object,
            user=request.user,
        )
        user_flagged = user_flag_qs.count() > 0
        context["user_flagged"] = user_flagged
        return self.render_to_response(context)

    def post(self, request, comment_id, next=None):
        self.object = self.get_object(comment_id)
        self.perform_flag()

        if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
            self.is_ajax = True
            template_list = self.get_template_names()
            context = self.get_context_data()
            status = 200
            return self.json_response(template_list, context, status)

        next_redirect_url = self.get_next_redirect_url(
            next or "comments-flag-done", c=self.object.pk
        )
        return http.HttpResponseRedirect(next_redirect_url)


@method_decorator([csrf_protect, login_required], name="dispatch")
class ReactToCommentView(SingleCommentView):
    http_method_names: ClassVar = ["get", "post"]
    check_option = "comments_reacting_enabled"
    template_alias = "react"
    template_alias_js = "reacted_js"
    context_object_name = "comment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["max_users_in_tooltip"] = getattr(
            settings, "COMMENTS_XTD_MAX_USERS_IN_TOOLTIP", 10
        )
        return context

    def perform_react(self):
        created = False  # Whether an instance of CommentReaction is created.
        operation = None  # 'add' or 'del' a reaction.
        reaction = self.request.POST["reaction"]
        creaction_qs = CommentReaction.objects.filter(
            reaction=reaction, comment=self.object
        )

        if creaction_qs.filter(authors=self.request.user).count() == 1:
            if creaction_qs[0].counter == 1:
                creaction_qs.delete()
            else:
                creaction_qs.update(counter=F("counter") - 1)
                creaction_qs[0].authors.remove(self.request.user)
            operation = "del"
        else:
            reaction_obj, created = CommentReaction.objects.get_or_create(
                reaction=reaction, comment=self.object
            )
            reaction_obj.authors.add(self.request.user)
            reaction_obj.counter += 1
            reaction_obj.save()
            operation = "add"

        djcx_signals.comment_got_a_reaction.send(
            sender=self.object.__class__,
            comment=self.object,
            reaction=reaction,
            created=created,
            operation=operation,
            request=self.request,
        )
        return created, operation

    def get(self, request, comment_id, next=None):
        self.object = self.get_object(comment_id)
        user_reactions_qs = CommentReaction.objects.filter(
            comment=self.object, authors=request.user
        )
        user_reactions = [
            get_reaction_enum()(reaction_obj.reaction)
            for reaction_obj in user_reactions_qs
        ]
        context = self.get_context_data(
            user_reactions=user_reactions, next=next
        )
        return self.render_to_response(context)

    def post(self, request, comment_id, next=None):
        self.object = self.get_object(comment_id)

        with transaction.atomic():
            created, operation = self.perform_react()

        if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
            self.is_ajax = True
            template_list = self.get_template_names()
            context = self.get_context_data()
            status = 201 if created else 200
            return self.json_response(template_list, context, status)

        next_redirect_url = self.get_next_redirect_url(
            next or "comments-xtd-react-done",
            c=self.object.pk,
        )
        request.session["reaction_op"] = operation
        return http.HttpResponseRedirect(next_redirect_url)


@method_decorator([csrf_protect, login_required], name="dispatch")
class ReactToCommentDoneView(SingleCommentView):
    http_method_names: ClassVar = [
        "get",
    ]
    check_option = "comments_reacting_enabled"
    template_alias = "reacted"
    context_object_name = "comment"

    def get(self, request):
        comment_id = request.GET.get("c", None)
        self.object = self.get_object(comment_id)
        context = self.get_context_data(
            object=self.object, operation=request.session.get("reaction_op")
        )
        return self.render_to_response(context)


class CommentReactionUserListView(ListView):
    http_method_names: ClassVar = ["get"]
    allow_empty = False
    paginate_by = settings.COMMENTS_XTD_NUM_COMMENT_REACTION_USERS_PER_PAGE
    ordering = settings.COMMENTS_XTD_COMMENT_REACTION_USERS_ORDER
    template_alias = "reaction_user_list"

    def get_queryset(self):
        self.queryset = self.reaction.authors
        return super().get_queryset()

    def get_template_names(self):
        return get_template_list(
            self.template_alias,
            app_label=self.object.content_object._meta.app_label,
            model=self.object.content_object._meta.model_name,
        )

    def get(self, request, comment_id, reaction_value):
        self.comment = get_object_or_404(
            get_model(),
            pk=comment_id,
            site__pk=utils.get_current_site_id(self.request),
        )
        self.reaction = get_object_or_404(
            CommentReaction, reaction=reaction_value, comment=self.comment
        )
        reaction_enum = get_reaction_enum()(self.reaction.reaction)

        self.object_list = self.get_queryset()

        max_users_in_tooltip = settings.COMMENTS_INK_MAX_USERS_IN_TOOLTIP
        if self.object_list.count() <= max_users_in_tooltip:
            raise http.Http404(_("Not enough users"))

        context = self.get_context_data(
            comment=self.comment, reaction=reaction_enum
        )
        return self.render_to_response(context)


# ---------------------------------------------------------
INVERSE_VOTE = {
    CommentVote.POSITIVE: CommentVote.NEGATIVE,
    CommentVote.NEGATIVE: CommentVote.POSITIVE,
}

VOTE_VALUE = {CommentVote.POSITIVE: +1, CommentVote.NEGATIVE: -1}


@method_decorator([csrf_protect, login_required], name="dispatch")
class VoteOnCommentView(SingleCommentView):
    http_method_names: ClassVar = ["get", "post"]
    check_option = "comments_voting_enabled"
    template_alias = "vote"
    template_alias_js = "voted_js"
    context_object_name = "comment"

    def get_object(self, comment_id):
        comment = super().get_object(comment_id)
        if comment.level > 0:
            raise http.Http404("Input is not allowed")
        return comment

    def perform_vote(self):
        delta = 0  # To sum to thread's score.
        vote = self.request.POST["vote"]
        vote_obj, created = CommentVote.objects.get_or_create(
            vote=vote, comment=self.object, author=self.request.user
        )

        if created:
            delta = CommentVote.VALUE[vote]
            counterpart_qs = CommentVote.objects.filter(
                vote=INVERSE_VOTE[vote],
                comment=self.object,
                author=self.request.user,
            )
            if counterpart_qs.count():
                delta += VOTE_VALUE[vote]
                counterpart_qs.delete()
        else:
            delta = -VOTE_VALUE[vote]
            vote_obj.delete()

        self.object.thread.score = self.object.thread.score + delta
        self.object.thread.save()

        djcx_signals.comment_got_a_vote.send(
            sender=self.object.__class__,
            comment=self.object,
            vote=vote,
            created=created,
            request=self.request,
        )
        return created

    def get(self, request, comment_id, next=None):
        self.object = self.get_object(comment_id)
        user_votes_qs = CommentVote.objects.filter(
            comment=self.object, author=request.user
        )
        user_vote = None if user_votes_qs.count() == 0 else user_votes_qs[0]
        context = self.get_context_data(user_vote=user_vote, next=next)
        return self.render_to_response(context)

    def post(self, request, comment_id, next=None):
        self.object = self.get_object(comment_id)

        with transaction.atomic():
            created = self.perform_vote()

        if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
            self.is_ajax = True
            request.session["djcx_highlight_cid"] = int(comment_id)
            template_list = self.get_template_names()
            context = self.get_context_data()
            status = 201 if created else 200
            return self.json_response(template_list, context, status)

        next_redirect_url = self.get_next_redirect_url(
            next or "comments-xtd-vote-done", c=self.object.pk
        )
        return http.HttpResponseRedirect(next_redirect_url)


@method_decorator([csrf_protect, login_required], name="dispatch")
class VoteOnCommentDoneView(SingleCommentView):
    http_method_names: ClassVar = [
        "get",
    ]
    check_option = "comments_voting_enabled"
    template_alias = "voted"
    context_object_name = "comment"

    def get_object(self, comment_id):
        comment = super().get_object(comment_id)
        if comment.level > 0:
            raise http.Http404("Input is not allowed")
        return comment

    def get(self, request):
        comment_id = request.GET.get("c", None)
        self.object = self.get_object(comment_id)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
