from django.db import models
from django.contrib.comments.models import Comment
from django.utils.translation import ugettext_lazy as _


class XtdComment(Comment):
    followup = models.BooleanField(help_text=_("Receive by email further comments in this conversation"), blank=True)


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
