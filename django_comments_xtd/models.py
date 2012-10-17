from django.db import models, transaction
from django.db.models import F, Max, Min
from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _


MAX_THREAD_LEVEL = getattr(settings, 'COMMENTS_XTD_MAX_THREAD_LEVEL', 0)
MAX_THREAD_LEVEL_BY_APP_MODEL = getattr(settings, 'COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL', {})


def max_thread_level_for_content_type(content_type):
    app_model = "%s.%s" % (content_type.app_label, content_type.model)
    if app_model in MAX_THREAD_LEVEL_BY_APP_MODEL:
        return MAX_THREAD_LEVEL_BY_APP_MODEL[app_model]
    else:
        return MAX_THREAD_LEVEL


class MaxThreadLevelExceededException(Exception):
    def __init__(self, content_type=None):
        self.max_by_app = max_thread_level_for_content_type(content_type)

    def __str__(self):
        return ugettext("Can not post comments over the thread level %{max_thread_level}") % {"max_thread_level": self.max_by_app}


class XtdCommentManager(models.Manager):
    def for_app_models(self, *args):
        """Return XtdComments for pairs "app.model" given in args"""
        content_types = []
        for app_model in args:
            app, model = app_model.split(".")
            content_types.append(ContentType.objects.get(app_label=app, 
                                                         model=model))
        return self.for_content_types(content_types)

    def for_content_types(self, content_types):
        qs = self.get_query_set().filter(content_type__in=content_types).reverse()
        return qs


class XtdComment(Comment):
    thread_id = models.IntegerField(default=0, db_index=True)
    parent_id = models.IntegerField(default=0)
    level = models.SmallIntegerField(default=0)
    order = models.IntegerField(default=1, db_index=True)
    followup = models.BooleanField(help_text=_("Receive by email further comments in this conversation"), blank=True)
    objects = XtdCommentManager()

    class Meta:
        ordering = ('thread_id', 'order')

    def save(self, *args, **kwargs):
        is_new = self.pk == None
        super(Comment, self).save(*args, **kwargs)
        if is_new:
            if not self.parent_id:
                self.parent_id = self.id
                self.thread_id = self.id
            else:
                if max_thread_level_for_content_type(self.content_type):
                    with transaction.commit_on_success():
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
        qc_eq_thread = XtdComment.objects.filter(thread_id = parent.thread_id)
        qc_ge_level = qc_eq_thread.filter(level__lte = parent.level,
                                          order__gt = parent.order)
        if qc_ge_level.count():
            min_order = qc_ge_level.aggregate(Min('order'))['order__min'] 
            XtdComment.objects.filter(thread_id = parent.thread_id,
                                      order__gte = min_order).update(order=F('order')+1)
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

class DummyDefaultManager:
    """
    Dummy Manager to mock django's CommentForm.check_for_duplicate method.
    """
    def __getattr__(self, name):
        return lambda *args, **kwargs: []
    
    def using(self, *args, **kwargs):
        return self

    # def __repr__(self):
    #     return ""


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
        return (TmpXtdComment, (), None, None, self.iteritems())
