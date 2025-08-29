#
# Two models: Article and Story. They have the same fields.
# The only difference is that Article do not have enabled
# flags, reactions and votes, while Story do have all them
# enabled.
#

from datetime import datetime

from django.db import models
from django.urls import reverse


class CommonProse(models.Model):
    title = models.CharField("title", max_length=200)
    slug = models.SlugField("slug", unique=True)
    body = models.TextField("body")
    allow_comments = models.BooleanField("allow comments", default=True)
    published_time = models.DateTimeField(
        "published time",
        default=datetime.now
    )

    class Meta:
        abstract = True
        ordering = ("-published_time",)

    def __str__(self):
        return self.title


# Articles do not allow comment flagging, votes, nor emotions. Also, the
# Detail template do not use django-comments-xtd JavaScript plugin. So
# comment form submission, comment preview, and comment reply, take place
# via backend.

class ArticleCommentsL0(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "articles_comments_l0"
        verbose_name_plural = "articles w/comments MTL-0"

    def get_absolute_url(self):
        return reverse(
            "article-comments-l0",
            kwargs={"slug": self.slug,}
        )


class ArticleCommentsL1(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "articles_comments_l1"
        verbose_name_plural = "articles w/comments MTL-1"

    def get_absolute_url(self):
        return reverse(
            "article-comments-l1",
            kwargs={"slug": self.slug,}
        )


class ArticleCommentsL2(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "articles_comments_l2"
        verbose_name_plural = "articles w/comments MTL-2"

    def get_absolute_url(self):
        return reverse(
            "article-comments-l2",
            kwargs={"slug": self.slug,}
        )


class ArticleCommentsL3(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "articles_comments_l3"
        verbose_name_plural = "articles w/comments MTL-3"

    def get_absolute_url(self):
        return reverse(
            "article-comments-l3",
            kwargs={"slug": self.slug,}
        )


# -------------------------------------------------------------------
# Stories allow comment flagging, votes, and emotions. Story's detail
# template do not use django-comments-xtd JavaScript plugin. So comment
# form submission, comment preview, comment reply, flagging, votes and
# emotions are take place
# via backend.


class StoryCommentsL0(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "stories_comments_l0"
        verbose_name_plural = "stories w/comments MTL-0"

    def get_absolute_url(self):
        return reverse(
            "story-comments-l0",
            kwargs={"slug": self.slug,}
        )


class StoryCommentsL1(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "stories_comments_l1"
        verbose_name_plural = "stories w/comments MTL-1"

    def get_absolute_url(self):
        return reverse(
            "story-comments-l1",
            kwargs={"slug": self.slug,}
        )


class StoryCommentsL2(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "stories_comments_l2"
        verbose_name_plural = "stories w/comments MTL-2"

    def get_absolute_url(self):
        return reverse(
            "story-comments-l2",
            kwargs={"slug": self.slug,}
        )


class StoryCommentsL3(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "stories_comments_l3"
        verbose_name_plural = "stories w/comments MTL-3"

    def get_absolute_url(self):
        return reverse(
            "story-comments-l3",
            kwargs={"slug": self.slug,}
        )


# -------------------------------------------------------------------
# Tales allow comment flagging, votes, and emotions. Tale's detail
# template use django-comments-xtd JavaScript plugin. So comment form
# submission, comment preview, comment reply, flagging, votes and emotions
# are sent via JavaScript.

class TaleCommentsL0(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "tales_comments_l0"
        verbose_name_plural = "tales w/comments MTL-0"

    def get_absolute_url(self):
        return reverse(
            "tale-comments-l0",
            kwargs={"slug": self.slug,}
        )


class TaleCommentsL1(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "tales_comments_l1"
        verbose_name_plural = "tales w/comments MTL-1"

    def get_absolute_url(self):
        return reverse(
            "tale-comments-l1",
            kwargs={"slug": self.slug,}
        )


class TaleCommentsL2(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "tales_comments_l2"
        verbose_name_plural = "tales w/comments MTL-2"

    def get_absolute_url(self):
        return reverse(
            "tale-comments-l2",
            kwargs={"slug": self.slug,}
        )


class TaleCommentsL3(CommonProse):
    class Meta(CommonProse.Meta):
        app_label = "prose"
        db_table = "tales_comments_l3"
        verbose_name_plural = "tales w/comments MTL-3"

    def get_absolute_url(self):
        return reverse(
            "tale-comments-l3",
            kwargs={"slug": self.slug,}
        )


def check_comments_input_allowed(obj):
    """
    Change the code to decide whether a quote `obj` can or cannot be commented.
    """
    # obj_date = obj.published_time.date()
    # obj_time = obj.published_time.time()
    # in2years_date = date(obj_date.year + 2, obj_date.month, obj_date.day)
    # in2years = timezone.make_aware(datetime.combine(in2years_date, obj_time))
    # if timezone.now() > in2years:
    #     return False
    # else:
    #     return True
    return obj.allow_comments
