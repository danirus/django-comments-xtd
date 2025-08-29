# ruff: noqa: I001

from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView

from django_comments import signals as djc_signals
from django_comments.forms import CommentSecurityForm

from django_comments_xtd import get_form, signed
from django_comments_xtd import signals as djcx_signals
from django_comments_xtd.models import TmpXtdComment, XtdComment
from django_comments_xtd.templating import get_template_list
from django_comments_xtd.views import ReactToCommentView, ReplyCommentView

from shared.users.decorators import not_authenticated
from prose.models import ArticleCommentsL0, ArticleCommentsL1
from prose.views import ProseDetailView


class HomepageView(TemplateView):
    template_name = "homepage.html"

    def get_context_data(self, **kwargs):
        if "cscheme" in self.request.session:
            self.request.session.pop("cscheme")
        return super().get_context_data(**kwargs)


class MockupView(DetailView):
    def get_object(self):
        article = ArticleCommentsL0.objects.get(pk=1)
        self.comment = XtdComment.objects.get(pk=1)
        return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.comment
        context['form'] = get_form()(
            self.comment.content_object, comment=self.comment
        )
        return context


# --------------------------------------------
def prose_v(model_name, slug, cscheme, theme=""):
    class _ProseDetailView(ProseDetailView):
        model = apps.get_model("prose", model_name)

        def get_object(self):
            return self.model.objects.get(slug=slug)

        def get_context_data(self, **kwargs):
            self.request.session['cscheme'] = self.cscheme
            return super().get_context_data(**kwargs)

    return _ProseDetailView.as_view(cscheme=cscheme, theme=theme)


def form_js_v(slug, cscheme, theme=""):
    """Force a form with errors submitted via JavaScript."""

    @method_decorator([not_authenticated], name='dispatch')
    class _FormJsView(ProseDetailView):
        model = ArticleCommentsL0
        template_name = "form_js_test.html"

        def get_object(self, *args, **kwargs):
            return ArticleCommentsL0.objects.get(slug=slug)

    return _FormJsView.as_view(cscheme=cscheme, theme=theme)


def bad_form_v(slug, cscheme, theme=""):
    """Force a bad form by removing a required security form field."""

    class _BadFormView(ProseDetailView):
        model = ArticleCommentsL0
        template_name = "bad_form_test.html"

        def get_object(self, *args, **kwargs):
            return ArticleCommentsL0.objects.get(slug=slug)

        def get_context_data(self, **kwargs):
            self.cscheme = cscheme
            self.theme = theme
            self.request.session['cscheme'] = self.cscheme
            context = super().get_context_data(**kwargs)
            context['form'] = get_form()(self.object, initial={
                "comment": (
                    "This comment form will fail, as it does not have "
                    "the field 'timestamp'. This way it is possible to "
                    "see the bad_form.html rendered."
                ),
                "name": "Joe Bloggs",
                "email": "joe@example.com"
            })
            # Remove a field, say "timestamp", so that validation fails.
            context['form'].fields.pop("timestamp")
            return context

    return _BadFormView.as_view()


def on_confirmation_accept_comment(sender, comment, request, **kwargs):
    return "discard this comment" not in comment['comment']

djcx_signals.confirmation_received.connect(on_confirmation_accept_comment)


def discard_comment_v(cscheme, theme=""):
    """Force the comment `discarded.html` template."""

    def _redirect(request):
        obj = ArticleCommentsL0.objects.get(pk=1)
        tmp_comment = TmpXtdComment(
            content_type=ContentType.objects.get_for_model(obj),
            object_pk=obj.pk,
            content_object=obj,
            site=Site.objects.get(pk=1),
            name="Joe Bloggs",
            email="joe@example.com",
            submit_date=datetime.now(),
            comment="discard this comment",
        )
        key = signed.dumps(
            tmp_comment,
            compress=True,
            extra_key=settings.COMMENTS_XTD_SALT
        )
        url = reverse("comments-xtd-confirm", args=(key.decode("utf-8"),))
        request.session['cscheme'] = cscheme
        return HttpResponseRedirect(url)

    return _redirect


def flag_comment_v(cscheme, theme=""):
    """Create a comment and redirect to flag it."""

    def _redirect(request):
        # Comment with pk=3 (sent to contenttype articles.storycommentsl1).
        url = reverse("comments-flag", args=(3,))
        request.session['cscheme'] = cscheme
        return HttpResponseRedirect(url)

    return _redirect


def moderated_v(cscheme, theme=""):
    class _ModeratedView(ProseDetailView):
        model = ArticleCommentsL0
        template_name = "comments/moderated.html"

        def get_object(self, *args, **kwargs):
            return ArticleCommentsL0.objects.get(pk=1)

        def get_context_data(self, **kwargs):
            self.cscheme = cscheme
            self.theme = theme
            self.request.session['cscheme'] = self.cscheme
            context = super().get_context_data(**kwargs)
            context['comment'] = XtdComment.objects.get(pk=1)
            return context

    return _ModeratedView.as_view()


def on_comment_will_be_posted(sender, comment, request, **kwargs):
    if "moderate this comment" in comment['comment']:
        comment['is_public'] = False
    return True

djc_signals.comment_will_be_posted.connect(on_comment_will_be_posted)


def moderated_js_v(slug, cscheme, theme=""):
    """Force rendering the `moderated_js.html` template."""

    class _ModerateJsView(ProseDetailView):
        model = ArticleCommentsL0
        template_name = "moderated_js_test.html"

        def get_object(self, *args, **kwargs):
            obj = ArticleCommentsL0.objects.get(slug=slug)
            # A bit of housekeeping: delete previous comments.
            ct = ContentType.objects.get_for_model(obj)
            prev = XtdComment.objects.filter(content_type=ct, object_pk=obj.pk)
            prev.delete()
            return obj

        def get_context_data(self, **kwargs):
            self.cscheme = cscheme
            self.theme = theme
            self.request.session['cscheme'] = self.cscheme
            context = super().get_context_data(**kwargs)
            context['form'] = get_form()(self.object, initial={
                "comment": (
                    "This comment has to be get the `is_public` "
                    "attribute to `False`, so that `PostCommentView` "
                    "sends a JsonResponse with the `moderated_js.html` "
                    "template. "
                    "So 'moderate this comment', please."
                ),
                "name": "Joe Bloggs",
                "email": "joe@example.com"
            })
            return context

    return _ModerateJsView.as_view()


def muted_v(cscheme, theme=""):
    """Force the comment `muted.html` template."""

    class _MutedView(TemplateView):
        template_name = "comments/muted.html"

        def get_context_data(self, **kwargs):
            self.cscheme = cscheme
            self.theme = theme
            self.request.session['cscheme'] = self.cscheme
            return super().get_context_data(
                comment=XtdComment.objects.get(pk=1),
                **kwargs
            )

    return _MutedView.as_view()


def posted_v(cscheme, theme=""):
    """Force the comment `posted.html` template."""

    class _PostedView(TemplateView):
        template_name = "comments/posted.html"

        def get_context_data(self, **kwargs):
            self.cscheme = cscheme
            self.theme = theme
            self.request.session['cscheme'] = self.cscheme
            return super().get_context_data(
                target=ArticleCommentsL0.objects.get(pk=1),
                **kwargs
            )

    return _PostedView.as_view()


def posted_js_v(slug, cscheme, theme=""):
    """Force render of `posted_js.html`, submitting comment via JavaScript."""

    @method_decorator([not_authenticated], name='dispatch')
    class _FormJsView(ProseDetailView):
        model = ArticleCommentsL0
        template_name = "posted_js_test.html"

        def get_object(self, *args, **kwargs):
            return ArticleCommentsL0.objects.get(slug=slug)

        def get_context_data(self, **kwargs):
            self.cscheme = cscheme
            self.theme = theme
            self.request.session['cscheme'] = self.cscheme
            context = super().get_context_data(**kwargs)
            context['form'] = get_form()(self.object, initial={
                "comment": (
                    "This comment form is sent directly in the template "
                    "`posted_js_test.html`, and rendered with the JS plugin."
                ),
                "name": "Joe Bloggs",
                "email": "joe@example.com",
            })
            return context

    return _FormJsView.as_view()


def published_js_v(slug, cscheme, theme=""):
    """Force render of `published_js.html`, submit comment via JavaScript."""

    @method_decorator([login_required], name='dispatch')
    class _FormJsView(ProseDetailView):
        model = ArticleCommentsL0
        template_name = "posted_js_test.html"

        def get_object(self, *args, **kwargs):
            obj = ArticleCommentsL0.objects.get(slug=slug)
            # A bit of housekeeping: delete previous comments.
            ct = ContentType.objects.get_for_model(obj)
            prev = XtdComment.objects.filter(content_type=ct, object_pk=obj.pk)
            prev.delete()
            return obj

        def get_context_data(self, **kwargs):
            self.cscheme = cscheme
            self.theme = theme
            self.request.session['cscheme'] = self.cscheme
            context = super().get_context_data(**kwargs)
            context['form'] = get_form()(self.object, initial={
                "comment": (
                    "This comment form is sent directly in the template "
                    "`posted_js_test.html`, to the article 'Force "
                    "published_js', and rendered with the JS plugin."
                ),
                "user": self.request.user,
            })
            return context

    return _FormJsView.as_view()


# --------------------------------------------
def reply_comment_v(cscheme, theme=""):

    class _ReplyCommentView(ReplyCommentView):
        def get(self, request, *args):
            self.cscheme = cscheme
            self.theme = theme
            self.request.session['cscheme'] = self.cscheme
            # comment.id should be 2, as comment with pk=2 is posted
            # to content-type 19 (ArticleCommentsL1). That model can
            # receive comments nested down to level 1.
            return super().get(request, 2)  # Comment with pk=2

    return _ReplyCommentView.as_view()


def reply_comment_ii_v(cscheme, theme=""):
    """
    This view returns the `reply.html` to reply the comment with `pk=3`,
    which is associated with the content type for model `StoryCommentsL1`,
    configured to accept flags, reactions and votes. So the `reply.html`
    should display them.
    """

    class _ReplyCommentView(ReplyCommentView):
        def get(self, request, *args):
            self.cscheme = cscheme
            self.theme = theme
            self.request.session['cscheme'] = self.cscheme
            # comment.id should be 3, as comment with pk=3 is posted
            # to content-type 23 (StoryCommentsL1). That model can
            # receive comments nested down to level 1.
            return super().get(request, 3)  # Comment with pk=3

    return _ReplyCommentView.as_view()


# --------------------------------------------
def preview_v(cscheme, theme="", reply_to=0):

    @method_decorator([not_authenticated], name='dispatch')
    class _PreviewCommentView(TemplateView):

        def get_template_names(self):
            kwds = {
                "app_label": "prose",
                "model": "articlecommentsl1",
            }
            if len(theme) > 0:
                kwds["theme"] = theme
            return get_template_list("preview", **kwds)

        def get_context_data(self, **kwargs):
            self.cscheme = cscheme
            self.theme = theme
            self.request.session['cscheme'] = self.cscheme
            context = super().get_context_data(**kwargs)
            obj = ArticleCommentsL1.objects.get(pk=1)
            secform = CommentSecurityForm(obj)
            form = get_form()(obj, data={
                "comment": (
                    "This comment form is sent in preview directly "
                    "in the template `form_js_test.html`, and rendered "
                    "with the JS plugin."
                ),
                "reply_to": f"{reply_to}",  # if != 0, it's the comment id.
                "name": "Joe Bloggs",
                "email": "joe@example.com",
                "timestamp": secform["timestamp"].value(),
                "security_hash": secform["security_hash"].value(),
            })
            form.is_valid()  # To produce `cleaned_data`, used in template.
            context["form"] = form
            return context

    return _PreviewCommentView.as_view()


def react_to_comment_v(cscheme, theme=""):

    class _ReplyCommentView(ReactToCommentView):
        def get(self, request, *args):
            self.cscheme = cscheme
            self.theme = theme
            self.request.session['cscheme'] = self.cscheme
            return super().get(request, 3)  # Comment pk=3 is for reactions.

    return _ReplyCommentView.as_view()

