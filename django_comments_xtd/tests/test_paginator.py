import collections
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
import pytest

from django_comments_xtd import get_model
from django_comments_xtd.paginator import CommentsPaginator


XtdComment = get_model()


def test_paginator_only_accepts_queryset():
    with pytest.raises(TypeError):
        CommentsPaginator([1,2,3], 10, 3)


@pytest.mark.django_db
def test_paginator_example_1(an_article):
    """Tests the Example 1 (detailed in the paginator.py __docs__)."""
    article_ct = ContentType.objects.get(app_label="tests", model="article")
    site = Site.objects.get(pk=1)
    attrs = {
        "content_type": article_ct,
        "object_pk": an_article.pk,
        "content_object": an_article,
        "site": site,
        "comment": f"another comment to article {an_article.pk}",
        "submit_date": datetime.now()
    }

    # Create 8 comments at level 0.
    for cm_level_0 in range(8):
        XtdComment.objects.create(**attrs)

    # Verify that the 8 comments are of level 0.
    cmts_level_0 = XtdComment.objects.all()
    for index, cm in enumerate(cmts_level_0):
        assert cm.pk == index + 1
        assert cm.level == 0
        assert cm.parent_id == cm.thread_id == cm.pk

    # Add the following number of child comments to the previous cmts_level_0.
    children_number = [10, 10, 10, 10, 10, 10, 5, 4]
    for index, cmt_level_0 in enumerate(cmts_level_0):
        for child in range(children_number[index]):
            XtdComment.objects.create(**attrs, parent_id=cmt_level_0.pk)

    # Verify that the children comments are nested into the cmts_level_0.
    cmts_level_0 = XtdComment.objects.filter(level=0)
    for index, cmt_level_0 in enumerate(cmts_level_0):
        assert cmt_level_0.pk == index + 1
        assert cmt_level_0.nested_count == children_number[index]

    # Test output from paginator.
    queryset = XtdComment.objects.all()
    page_size = 25
    orphans = 10
    paginator = CommentsPaginator(queryset, page_size, orphans)
    assert paginator.count == queryset.count()

    # Page 1 shall contain 22 comments.
    page = paginator.page(1)
    assert page.object_list.count() == 22
    comment_list = [cm.parent_id for cm in page.object_list]
    assert set(comment_list) == set([1, 2])
    counter = collections.Counter(comment_list)
    assert counter[1] == 11
    assert counter[2] == 11

    # Page 2 shall contain 22 comments.
    page = paginator.page(2)
    assert page.object_list.count() == 22
    comment_list = [cm.parent_id for cm in page.object_list]
    assert set(comment_list) == set([3, 4])
    counter = collections.Counter(comment_list)
    assert counter[3] == 11
    assert counter[4] == 11

    # Page 3 shall contain 22 comments.
    page = paginator.page(3)
    assert page.object_list.count() == 33
    comment_list = [cm.parent_id for cm in page.object_list]
    assert set(comment_list) == set([5, 6, 7, 8])
    counter = collections.Counter(comment_list)
    assert counter[5] == 11
    assert counter[6] == 11
    assert counter[7] == 6
    assert counter[8] == 5


@pytest.mark.django_db
def test_paginator_example_2(an_article):
    """Tests the Example 2 (detailed in the paginator.py __docs__)."""
    article_ct = ContentType.objects.get(app_label="tests", model="article")
    site = Site.objects.get(pk=1)
    attrs = {
        "content_type": article_ct,
        "object_pk": an_article.pk,
        "content_object": an_article,
        "site": site,
        "comment": f"another comment to article {an_article.pk}",
        "submit_date": datetime.now()
    }

    # Create 3 comments at level 0.
    for cm_level_0 in range(3):
        XtdComment.objects.create(**attrs)

    # Verify that the 3 comments are of level 0.
    cmts_level_0 = XtdComment.objects.all()
    for index, cm in enumerate(cmts_level_0):
        assert cm.pk == index + 1
        assert cm.level == 0
        assert cm.parent_id == cm.thread_id == cm.pk

    # Add the following number of child comments to the previous cmts_level_0.
    children_number = [24, 24, 8]
    for index, cmt_level_0 in enumerate(cmts_level_0):
        for child in range(children_number[index]):
            XtdComment.objects.create(**attrs, parent_id=cmt_level_0.pk)

    # Verify that the children comments are nested into the cmts_level_0.
    cmts_level_0 = XtdComment.objects.filter(level=0)
    for index, cmt_level_0 in enumerate(cmts_level_0):
        assert cmt_level_0.pk == index + 1
        assert cmt_level_0.nested_count == children_number[index]

    # Test output from paginator.
    queryset = XtdComment.objects.all()
    page_size = 25
    orphans = 10
    paginator = CommentsPaginator(queryset, page_size, orphans)
    assert paginator.count == queryset.count()

    # Page 1 shall contain 25 comments.
    page = paginator.page(1)
    assert page.object_list.count() == 25
    comment_list = [cm.parent_id for cm in page.object_list]
    assert set(comment_list) == set([1])
    counter = collections.Counter(comment_list)
    assert counter[1] == 25

    # Page 2 shall contain 22 comments.
    page = paginator.page(2)
    assert page.object_list.count() == 34
    comment_list = [cm.parent_id for cm in page.object_list]
    assert set(comment_list) == set([2, 3])
    counter = collections.Counter(comment_list)
    assert counter[2] == 25
    assert counter[3] == 9


@pytest.mark.django_db
def test_paginator_example_3(an_article):
    """Tests the Example 3 (detailed in the paginator.py __docs__)."""
    article_ct = ContentType.objects.get(app_label="tests", model="article")
    site = Site.objects.get(pk=1)
    attrs = {
        "content_type": article_ct,
        "object_pk": an_article.pk,
        "content_object": an_article,
        "site": site,
        "comment": f"another comment to article {an_article.pk}",
        "submit_date": datetime.now()
    }

    # Create 3 comments at level 0.
    for cm_level_0 in range(3):
        XtdComment.objects.create(**attrs)

    # Verify that the 3 comments are of level 0.
    cmts_level_0 = XtdComment.objects.all()
    for index, cm in enumerate(cmts_level_0):
        assert cm.pk == index + 1
        assert cm.level == 0
        assert cm.parent_id == cm.thread_id == cm.pk

    # Add the following number of child comments to the previous cmts_level_0.
    children_number = [24, 8, 8]
    for index, cmt_level_0 in enumerate(cmts_level_0):
        for child in range(children_number[index]):
            XtdComment.objects.create(**attrs, parent_id=cmt_level_0.pk)

    # Verify that the children comments are nested into the cmts_level_0.
    cmts_level_0 = XtdComment.objects.filter(level=0)
    for index, cmt_level_0 in enumerate(cmts_level_0):
        assert cmt_level_0.pk == index + 1
        assert cmt_level_0.nested_count == children_number[index]

    # Test output from paginator.
    queryset = XtdComment.objects.all()
    page_size = 25
    orphans = 10
    paginator = CommentsPaginator(queryset, page_size, orphans)
    assert paginator.count == queryset.count()

    # Page 1 shall contain 25 comments.
    page = paginator.page(1)
    assert page.object_list.count() == 25
    comment_list = [cm.parent_id for cm in page.object_list]
    assert set(comment_list) == set([1])
    counter = collections.Counter(comment_list)
    assert counter[1] == 25

    # Page 2 shall contain 22 comments.
    page = paginator.page(2)
    assert page.object_list.count() == 18
    comment_list = [cm.parent_id for cm in page.object_list]
    assert set(comment_list) == set([2, 3])
    counter = collections.Counter(comment_list)
    assert counter[2] == 9
    assert counter[3] == 9


@pytest.mark.django_db
def test_paginator_allow_empty_first_page():
    qs = XtdComment.objects.all()
    paginator = CommentsPaginator(qs, 10, orphans=3,
                                  allow_empty_first_page=False)
    assert paginator.num_pages == 0
