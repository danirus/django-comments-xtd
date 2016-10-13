import six

import django
from django.db import models
from django.db.models import F, Max, Min
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext, ugettext_lazy as _

try:
    from django.db.transaction import atomic
except ImportError:
    from django.db.transaction import commit_on_success as atomic

try:
    from django_comments.managers import CommentManager
    from django_comments.models import Comment
except ImportError:
    from django.contrib.comments.managers import CommentManager
    from django.contrib.comments.models import Comment

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
    def __init__(self, content_type=None):
        self.max_by_app = max_thread_level_for_content_type(content_type)

    def __str__(self):
        return (ugettext("Can not post comments over the thread level "
                         "%{max_thread_level}") %
                {"max_thread_level": self.max_by_app})


class XtdCommentManager(CommentManager):
    if django.VERSION[:2] < (1, 6):
        get_queryset = models.Manager.get_query_set

    def for_app_models(self, *args):
        """Return XtdComments for pairs "app.model" given in args"""
        content_types = []
        for app_model in args:
            app, model = app_model.split(".")
            content_types.append(ContentType.objects.get(app_label=app,
                                                         model=model))
        return self.for_content_types(content_types)

    def for_content_types(self, content_types):
        qs = self.get_queryset().filter(content_type__in=content_types)\
                                .reverse()
        return qs


class XtdComment(Comment):
    thread_id = models.IntegerField(default=0, db_index=True)
    parent_id = models.IntegerField(default=0)
    level = models.SmallIntegerField(default=0)
    order = models.IntegerField(default=1, db_index=True)
    followup = models.BooleanField(blank=True, default=False,
                                   help_text=_("Receive by email further "
                                               "comments in this conversation"))
    objects = XtdCommentManager()

    class Meta:
        ordering = settings.COMMENTS_XTD_LIST_ORDER

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
                    raise MaxThreadLevelExceededException(self.content_type)
            kwargs["force_insert"] = False
            super(Comment, self).save(*args, **kwargs)

    def _calculate_thread_data(self):
        # Implements the following approach:
        #  http://www.sqlteam.com/article/sql-for-threaded-discussion-forums
        parent = XtdComment.objects.get(pk=self.parent_id)
        if parent.level == max_thread_level_for_content_type(self.content_type):
            raise MaxThreadLevelExceededException(self.content_type)

        self.thread_id = parent.thread_id
        self.level = parent.level + 1
        qc_eq_thread = XtdComment.objects.filter(thread_id=parent.thread_id)
        qc_ge_level = qc_eq_thread.filter(level__lte=parent.level,
                                          order__gt=parent.order)
        if qc_ge_level.count():
            min_order = qc_ge_level.aggregate(Min('order'))['order__min']
            XtdComment.objects.filter(thread_id=parent.thread_id,
                                      order__gte=min_order)\
                              .update(order=F('order')+1)
            self.order = min_order
        else:
            max_order = qc_eq_thread.aggregate(Max('order'))['order__max']
            self.order = max_order + 1

    @models.permalink
    def get_reply_url(self):
        return ("comments-xtd-reply", None, {"cid": self.pk})

    def allow_thread(self):
        if self.level < max_thread_level_for_content_type(self.content_type):
            return True
        else:
            return False

    @classmethod
    def tree_from_queryset(cls, queryset, with_participants=False):
        """Converts a XtdComment queryset into a list of nested dictionaries.
        The queryset has to be ordered by thread_id, order.
        Each dictionary contains two attributes::
            {
                'comment': the comment object itself,
                'children': [list of child comment dictionaries]
            }
        """
        def get_participants(comment):
            return {'likedit': comment.users_who_liked_it(),
                    'dislikedit': comment.users_who_disliked_it()}

        def add_children(children, obj):
            for item in children:
                if item['comment'].pk == obj.parent_id:
                    child_dict = {'comment': obj, 'children': []}
                    if with_participants:
                        child_dict.update(get_participants(obj))
                    item['children'].append(child_dict)
                    return True
                elif item['children']:
                    if add_children(item['children'], obj):
                        return True
            return False

        dic_list = []
        cur_dict = None
        for obj in queryset:
            # A new comment at the same level as thread_dict.
            if cur_dict and obj.level == cur_dict['comment'].level:
                dic_list.append(cur_dict)
                cur_dict = None
            if not cur_dict:
                cur_dict = {'comment': obj, 'children': []}
                if with_participants:
                    cur_dict.update(get_participants(obj))
                continue
            if obj.parent_id == cur_dict['comment'].pk:
                child_dict = {'comment': obj, 'children': []}
                if with_participants:
                    child_dict.update(get_participants(obj))
                cur_dict['children'].append(child_dict)
            else:
                add_children(cur_dict['children'], obj)
        if cur_dict:
            dic_list.append(cur_dict)
        return dic_list

    def users_who_liked_it(self):
        return [flag.user for flag in self.flags.filter(flag=LIKEDIT_FLAG)]

    def users_who_disliked_it(self):
        return [flag.user for flag in self.flags.filter(flag=DISLIKEDIT_FLAG)]


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
            return ""

    def __reduce__(self):
        return (TmpXtdComment, (), None, None, six.iteritems(self))


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
