from django.db import models
from django.db.models import F, Max, Min, Q
from django.db.transaction import atomic
from django.contrib.contenttypes.models import ContentType
from django.core import signing
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from django_comments.managers import CommentManager
from django_comments.models import Comment, CommentFlag
from django_comments.signals import comment_was_flagged

from django_comments_xtd.conf import settings


LIKEDIT_FLAG = "I liked it"
DISLIKEDIT_FLAG = "I disliked it"


def max_thread_level_for_content_type(content_type):
    app_model = "%s.%s" % (content_type.app_label, content_type.model)
    if app_model in settings.COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL:
        return settings.COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL[app_model]
    else:
        return settings.COMMENTS_XTD_MAX_THREAD_LEVEL


class MaxThreadLevelExceededException(Exception):
    def __init__(self, comment):
        self.comment = comment
        # self.max_by_app = max_thread_level_for_content_type(content_type)

    def __str__(self):
        return ("Max thread level reached for comment %d" % self.comment.id)


class XtdCommentManager(CommentManager):

    def for_app_models(self, *args, **kwargs):
        """Return XtdComments for pairs "app.model" given in args"""
        content_types = []
        for app_model in args:
            app, model = app_model.split(".")
            content_types.append(ContentType.objects.get(app_label=app,
                                                         model=model))
        return self.for_content_types(content_types, **kwargs)

    def for_content_types(self, content_types, site=None):
        filter_fields = {'content_type__in': content_types}
        if site is not None:
            filter_fields['site'] = site
        qs = self.get_queryset().filter(**filter_fields)\
                                .reverse()
        return qs

    def get_queryset(self):
        qs = super(XtdCommentManager, self).get_queryset()
        return qs.\
            select_related('user', 'content_type').\
            order_by(*settings.COMMENTS_XTD_LIST_ORDER)


class XtdComment(Comment):
    thread_id = models.IntegerField(default=0, db_index=True)
    parent_id = models.IntegerField(default=0)
    level = models.SmallIntegerField(default=0)
    order = models.IntegerField(default=1, db_index=True)
    followup = models.BooleanField(blank=True, default=False,
                                   help_text=_("Notify follow-up comments"))
    objects = XtdCommentManager()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(Comment, self).save(*args, **kwargs)
        if is_new:
            if not self.parent_id:
                self.parent_id = self.id
                self.thread_id = self.id
            else:
                if max_thread_level_for_content_type(self.content_type):
                    with atomic():
                        self._calculate_thread_data()
                else:
                    raise MaxThreadLevelExceededException(self)
            kwargs["force_insert"] = False
            super(Comment, self).save(*args, **kwargs)

    def _calculate_thread_data(self):
        # Implements the following approach:
        #  http://www.sqlteam.com/article/sql-for-threaded-discussion-forums
        parent = XtdComment.objects.get(pk=self.parent_id)
        if parent.level == max_thread_level_for_content_type(self.content_type):
            raise MaxThreadLevelExceededException(self)

        self.thread_id = parent.thread_id
        self.level = parent.level + 1
        qc_eq_thread = XtdComment.objects.filter(thread_id=parent.thread_id)
        qc_ge_level = qc_eq_thread.filter(level__lte=parent.level,
                                          order__gt=parent.order)
        if qc_ge_level.count():
            min_order = qc_ge_level.aggregate(Min('order'))['order__min']
            XtdComment.objects.filter(thread_id=parent.thread_id,
                                      order__gte=min_order)\
                              .update(order=F('order') + 1)
            self.order = min_order
        else:
            max_order = qc_eq_thread.aggregate(Max('order'))['order__max']
            self.order = max_order + 1

    def get_reply_url(self):
        return reverse("comments-xtd-reply", kwargs={"cid": self.pk})

    def allow_thread(self):
        if self.level < max_thread_level_for_content_type(self.content_type):
            return True
        else:
            return False

    @classmethod
    def tree_from_queryset(cls, queryset, with_flagging=False,
                           with_feedback=False, user=None):
        """Converts a XtdComment queryset into a list of nested dictionaries.
        The queryset has to be ordered by thread_id, order.
        Each dictionary contains two attributes::
            {
                'comment': the comment object itself,
                'children': [list of child comment dictionaries]
            }
        """
        def get_user_feedback(comment, user):
            d = {'likedit_users': comment.users_flagging(LIKEDIT_FLAG),
                 'dislikedit_users': comment.users_flagging(DISLIKEDIT_FLAG)}
            if user is not None:
                if user in d['likedit_users']:
                    d['likedit'] = True
                if user in d['dislikedit_users']:
                    d['dislikedit'] = True
            return d

        def add_children(children, obj, user):
            for item in children:
                if item['comment'].pk == obj.parent_id:
                    child_dict = {'comment': obj, 'children': []}
                    if with_feedback:
                        child_dict.update(get_user_feedback(obj, user))
                    item['children'].append(child_dict)
                    return True
                elif item['children']:
                    if add_children(item['children'], obj, user):
                        return True
            return False

        def get_new_dict(obj):
            new_dict = {'comment': obj, 'children': []}
            if with_feedback:
                new_dict.update(get_user_feedback(obj, user))
            if with_flagging:
                users_flagging = obj.users_flagging(CommentFlag.SUGGEST_REMOVAL)
                if user.has_perm('django_comments.can_moderate'):
                    new_dict.update({'flagged_count': len(users_flagging)})
                new_dict.update({'flagged': user in users_flagging})
            return new_dict

        dic_list = []
        cur_dict = None
        for obj in queryset:
            if cur_dict and obj.level == cur_dict['comment'].level:
                dic_list.append(cur_dict)
                cur_dict = None
            if not cur_dict:
                cur_dict = get_new_dict(obj)
                continue
            if obj.parent_id == cur_dict['comment'].pk:
                child_dict = get_new_dict(obj)
                cur_dict['children'].append(child_dict)
            else:
                add_children(cur_dict['children'], obj, user)
        if cur_dict:
            dic_list.append(cur_dict)
        return dic_list

    def users_flagging(self, flag):
        return [obj.user for obj in self.flags.filter(flag=flag)]


@receiver(comment_was_flagged)
def unpublish_nested_comments_on_removal_flag(sender, comment, flag, **kwargs):
    if flag.flag == CommentFlag.MODERATOR_DELETION:
        XtdComment.objects.filter(~(Q(pk=comment.id)), parent_id=comment.id)\
                          .update(is_public=False)


class DummyDefaultManager:
    """
    Dummy Manager to mock django's CommentForm.check_for_duplicate method.
    """
    def __getattr__(self, name):
        return lambda *args, **kwargs: []

    def using(self, *args, **kwargs):
        return self


class TmpXtdComment(dict):
    """
    Temporary XtdComment to be pickled, ziped and appended to a URL.
    """
    _default_manager = DummyDefaultManager()

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value

    def save(self, *args, **kwargs):
        pass

    def _get_pk_val(self):
        if self.xtd_comment:
            return self.xtd_comment._get_pk_val()
        else:
            content_type = "%s.%s" % self.content_type.natural_key()
            return signing.dumps("%s:%s" % (content_type, self.object_pk))

    def __setstate__(self, state):
        ct_key = state.pop('content_type_key')
        ctype = ContentType.objects.get_by_natural_key(*ct_key)
        self.update(
            state,
            content_type=ctype,
            content_object=ctype.get_object_for_this_type(
                pk=state['object_pk']
            )
        )

    def __reduce__(self):
        state = {k: v for k, v in self.items() if k != 'content_object'}
        ct = state.pop('content_type')
        state['content_type_key'] = ct.natural_key()
        return (TmpXtdComment, (), state)


# ----------------------------------------------------------------------
class BlackListedDomain(models.Model):
    """
    A blacklisted domain from which comments should be discarded.
    Automatically populated with a small amount of spamming domains,
    gathered from http://www.joewein.net/spam/blacklist.htm

    You can download for free a recent version of the list, and subscribe
    to get notified on changes. Changes can be fetched with rsync for a
    small fee (check their conditions, or use any other Spam filter).
    """
    domain = models.CharField(max_length=200, db_index=True)

    def __str__(self):
        return self.domain

    class Meta:
        ordering = ('domain',)
