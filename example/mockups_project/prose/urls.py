from django.urls import path

from .models import (
    ArticleCommentsL0,
    ArticleCommentsL1,
    ArticleCommentsL2,
    ArticleCommentsL3,
    StoryCommentsL0,
    StoryCommentsL1,
    StoryCommentsL2,
    StoryCommentsL3,
    TaleCommentsL0,
    TaleCommentsL1,
    TaleCommentsL2,
    TaleCommentsL3,
)
from .views import ProseDetailView

urlpatterns = [
    # -----------------------
    # With `Article*` models.
    path(
        "article-comments-l0/<slug:slug>/",
        ProseDetailView.as_view(model=ArticleCommentsL0),
        name="article-comments-l0"
    ),
    path(
        "article-comments-l1/<slug:slug>/",
        ProseDetailView.as_view(model=ArticleCommentsL1),
        name="article-comments-l1"
    ),
    path(
        "article-comments-l2/<slug:slug>/",
        ProseDetailView.as_view(model=ArticleCommentsL2),
        name="article-comments-l2"
    ),
    path(
        "article-comments-l3/<slug:slug>/",
        ProseDetailView.as_view(model=ArticleCommentsL3),
        name="article-comments-l3"
    ),

    # -----------------------
    # With `Story*` models.
    path(
        "story-comments-l0/<slug:slug>/",
        ProseDetailView.as_view(model=StoryCommentsL0),
        name="story-comments-l0"
    ),
    path(
        "story-comments-l1/<slug:slug>/",
        ProseDetailView.as_view(model=StoryCommentsL1),
        name="story-comments-l1"
    ),
    path(
        "story-comments-l2/<slug:slug>/",
        ProseDetailView.as_view(model=StoryCommentsL2),
        name="story-comments-l2"
    ),
    path(
        "story-comments-l3/<slug:slug>/",
        ProseDetailView.as_view(model=StoryCommentsL3),
        name="story-comments-l3"
    ),

    # -----------------------
    # With `Tale*` models.
    path(
        "tale-comments-l0/<slug:slug>/",
        ProseDetailView.as_view(model=TaleCommentsL0),
        name="tale-comments-l0"
    ),
    path(
        "tale-comments-l1/<slug:slug>/",
        ProseDetailView.as_view(model=TaleCommentsL1),
        name="tale-comments-l1"
    ),
    path(
        "tale-comments-l2/<slug:slug>/",
        ProseDetailView.as_view(model=TaleCommentsL2),
        name="tale-comments-l2"
    ),
    path(
        "tale-comments-l3/<slug:slug>/",
        ProseDetailView.as_view(model=TaleCommentsL3),
        name="tale-comments-l3"
    ),
]
