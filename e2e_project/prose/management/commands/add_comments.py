# ruff: noqa: RUF100, PLR0913
from datetime import datetime, timedelta
from random import randint

import pytz
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from lorem_text import lorem
from shared.users.models import User

from django_comments_xtd.models import CommentReaction, XtdComment

content_parameters = [
    {
        "model": "ArticleCommentsL0",
        "slug": "one-comment-options-off",
        "comments": 1,
        "reactions": [],
    },
    {  # Do not move this comment (it is expected to get pk=2)
        "model": "ArticleCommentsL1",
        "slug": "reply-to-comment",
        "comments": 1,
        "reactions": [],
    },
    {  # Do not move this comment (it is expected to get pk=3)
        "model": "StoryCommentsL1",
        "slug": "reply-to-comment",
        "comments": 1,
        "reactions": [  # Each entry is the list of reactions for each comment.
            [("+", 5), ("H", 2)],  # Reactions to first comment.
        ],
    },
    {
        "model": "StoryCommentsL0",
        "slug": "one-comment-options-on",
        "comments": 1,
        "reactions": [  # Each entry is the list of reactions for each comment.
            [("+", 3), ("S", 2), ("H", 1)],  # Reactions to first comment.
        ],
    },
    {
        "model": "TaleCommentsL0",
        "slug": "one-comment-options-on-js",
        "comments": 1,
        "reactions": [  # Each entry is the list of reactions for each comment.
            [("+", 3), ("S", 2), ("H", 1)],  # Reactions to first comment.
        ],
    },
    {
        "model": "ArticleCommentsL0",
        "slug": "n-comments-options-off",
        "comments": 4,
        "reactions": [],  # Articles do not allow reactions.
    },
    {
        "model": "StoryCommentsL0",
        "slug": "n-comments-options-on",
        "comments": 4,
        "reactions": [
            [("+", 8), ("R", 1)],
            [("+", 5), ("G", 4)],
            [("-", 3), ("E", 2)],
            [("H", 4)],
        ],
    },
    {
        "model": "TaleCommentsL0",
        "slug": "n-comments-options-on-js",
        "comments": 4,
        "reactions": [
            [("+", 8), ("R", 3), ("G", 2)],
            [("+", 5), ("G", 4)],
            [("-", 3), ("E", 2)],
            [("H", 4)],
        ],
    },
    {
        "model": "ArticleCommentsL1",
        "slug": "n-comments-options-off",
        "comments": [  # This represents nested comments.
            (1,),  # First level tuples are comments at level 0.
            (2, (3, 4)),  # Here 3 and 4 are replies at level 1.
            (5, (6, 7, 8)),  # Here 6, 7 and 8 are replies at level 1.
        ],
        "reactions": [],  # Articles do not allow reactions.
    },
    {
        "model": "StoryCommentsL1",
        "slug": "n-comments-options-on",
        "comments": [  # This represents nested comments.
            (1,),  # First level tuples are comments at level 0.
            (2, (3, 4)),  # Here 3 and 4 are replies at level 1.
            (5, (6, 7, 8)),  # Here 6, 7 and 8 are replies at level 1.
        ],
        "reactions": [
            [("+", 14), ("R", 8), ("S", 3), ("G", 2)],  # reactions for 1
            [("+", 8), ("S", 5), ("G", 1)],  # reactions for 2
            [("-", 9), ("E", 7)],  # reactions for 3
            [("+", 4), ("S", 3)],  # reactions for 4
            [("+", 4), ("R", 3), ("G", 1)],  # reactions for 5
            [("+", 5), ("G", 4)],  # reactions for 6
            [("-", 3), ("E", 2)],  # reactions for 7
            [("+", 12), ("H", 9)],  # reactions for 8
        ],  # Articles do not allow reactions.
    },
    {
        "model": "TaleCommentsL1",
        "slug": "n-comments-options-on-js",
        "comments": [  # This represents nested comments.
            (1,),  # First level tuples are comments at level 0.
            (2, (3, 4)),  # Here 3 and 4 are replies at level 1.
            (5, (6, 7, 8)),  # Here 6, 7 and 8 are replies at level 1.
        ],
        "reactions": [
            [("+", 14), ("R", 8), ("S", 3), ("G", 2)],  # reactions for 1
            [("+", 8), ("S", 5), ("G", 1)],  # reactions for 2
            [("-", 9), ("E", 7)],  # reactions for 3
            [("+", 4), ("S", 3)],  # reactions for 4
            [("+", 4), ("R", 3), ("G", 1)],  # reactions for 5
            [("+", 5), ("G", 4)],  # reactions for 6
            [("-", 3), ("E", 2)],  # reactions for 7
            [("+", 12), ("H", 9)],  # reactions for 8
        ],  # Articles do not allow reactions.
    },
    {
        "model": "ArticleCommentsL2",
        "slug": "n-comments-options-off",
        "comments": [  # This represents nested comments.
            (1, (2, (3,), 4)),
            (5, (6, (7, 8, 9), 10)),
            (11, (12, 13, (14, 15))),
        ],
        "reactions": [],  # Articles do not allow reactions.
    },
    {
        "model": "StoryCommentsL2",
        "slug": "n-comments-options-on",
        "comments": [  # This represents nested comments.
            (1, (2, (3,), 4)),
            (5, (6, (7, 8, 9), 10)),
            (11, (12, 13, (14, 15))),
        ],
        "reactions": [
            [("+", 14), ("R", 8), ("S", 3), ("G", 2)],  # reactions for 1
            [("+", 8), ("S", 5), ("G", 1)],  # reactions for 2
            [("-", 9), ("E", 7)],  # reactions for 3
            [("+", 4), ("S", 3)],  # reactions for 4
            [("+", 4), ("R", 3), ("G", 1)],  # reactions for 5
            [("+", 5), ("G", 4)],  # reactions for 6
            [("-", 3), ("E", 2)],  # reactions for 7
            [("+", 12), ("H", 9)],  # reactions for 8
            [("G", 14), ("C", 5)],  # reactions for 9
            [("+", 25), ("R", 6), ("C", 2)],  # reactions for 10
            [("+", 13), ("G", 1)],  # reactions for 11
            [
                ("+", 3),
            ],  # reactions for 12
            [("G", 32), ("+", 22), ("H", 12)],  # reactions for 13
            [("+", 11), ("H", 1)],  # reactions for 14
            [("+", 6), ("R", 6), ("H", 6)],  # reactions for 15
        ],
    },
    {
        "model": "TaleCommentsL2",
        "slug": "n-comments-options-on-js",
        "comments": [  # This represents nested comments.
            (1, (2, (3,), 4)),
            (5, (6, (7, 8, 9), 10)),
            (11, (12, 13, (14, 15))),
        ],
        "reactions": [
            [("+", 14), ("R", 8), ("S", 3), ("G", 2)],  # reactions for 1
            [("+", 8), ("S", 5), ("G", 1)],  # reactions for 2
            [("-", 9), ("E", 7)],  # reactions for 3
            [("+", 4), ("S", 3)],  # reactions for 4
            [("+", 4), ("R", 3), ("G", 1)],  # reactions for 5
            [("+", 5), ("G", 4)],  # reactions for 6
            [("-", 3), ("E", 2)],  # reactions for 7
            [("+", 12), ("H", 9)],  # reactions for 8
            [("G", 14), ("C", 5)],  # reactions for 9
            [("+", 25), ("R", 6), ("C", 2)],  # reactions for 10
            [("+", 13), ("G", 1)],  # reactions for 11
            [
                ("+", 3),
            ],  # reactions for 12
            [("G", 32), ("+", 22), ("H", 12)],  # reactions for 13
            [("+", 11), ("H", 1)],  # reactions for 14
            [("+", 6), ("R", 6), ("H", 6)],  # reactions for 15
        ],
    },
    {
        "model": "ArticleCommentsL3",
        "slug": "n-comments-options-off",
        "comments": [  # This represents nested comments.
            (1, (2, (3, (4, 5), 6, 7, (8, 9)))),
            (10, (11, (12, (13, 14), 15, (16, 17), 18))),
        ],
        "reactions": [],
    },
    {
        "model": "StoryCommentsL3",
        "slug": "n-comments-options-on",
        "comments": [  # This represents nested comments.
            (1, (2, (3, (4, 5), 6, 7), 8, 9)),
            (10, (11, (12, 13, 14), 15, 16, (17, 18))),
        ],
        "reactions": [
            [("+", 14), ("R", 8), ("S", 3), ("G", 2)],  # reactions for 1
            [("+", 8), ("S", 5), ("G", 1)],  # reactions for 2
            [("-", 9), ("E", 7)],  # reactions for 3
            [("+", 4), ("S", 3)],  # reactions for 4
            [("+", 4), ("R", 3), ("G", 1)],  # reactions for 5
            [("+", 5), ("G", 4)],  # reactions for 6
            [("-", 3), ("E", 2)],  # reactions for 7
            [("+", 12), ("H", 9)],  # reactions for 8
            [("G", 14), ("C", 5)],  # reactions for 9
            [("+", 25), ("R", 6), ("C", 2)],  # reactions for 10
            [("+", 13), ("G", 1)],  # reactions for 11
            [
                ("+", 9),
            ],  # reactions for 12
            [("G", 32), ("+", 22), ("H", 12)],  # reactions for 13
            [("+", 11), ("H", 1)],  # reactions for 14
            [("+", 6), ("R", 6), ("H", 6)],  # reactions for 15
            [("+", 19), ("R", 5), ("G", 3)],  # reactions for 16
            [("-", 16), ("E", 8), ("C", 7)],  # reactions for 17
            [
                ("+", 3),
            ],  # reactions for 18
        ],
    },
    {
        "model": "TaleCommentsL3",
        "slug": "n-comments-options-on-js",
        "comments": [  # This represents nested comments.
            (1, (2, (3, (4, 5), 6, 7), 8, 9)),
            (10, (11, (12, 13, 14), 15, 16, (17, 18))),
        ],
        "reactions": [
            [("+", 14), ("R", 8), ("S", 3), ("G", 2)],  # reactions for 1
            [("+", 8), ("S", 5), ("G", 1)],  # reactions for 2
            [("-", 9), ("E", 7)],  # reactions for 3
            [("+", 4), ("S", 3)],  # reactions for 4
            [("+", 4), ("R", 3), ("G", 1)],  # reactions for 5
            [("+", 5), ("G", 4)],  # reactions for 6
            [("-", 3), ("E", 2)],  # reactions for 7
            [("+", 12), ("H", 9)],  # reactions for 8
            [("G", 14), ("C", 5)],  # reactions for 9
            [("+", 25), ("R", 6), ("C", 2)],  # reactions for 10
            [("+", 13), ("G", 1)],  # reactions for 11
            [
                ("+", 9),
            ],  # reactions for 12
            [("G", 32), ("+", 22), ("H", 12)],  # reactions for 13
            [("+", 11), ("H", 1)],  # reactions for 14
            [("+", 6), ("R", 6), ("H", 6)],  # reactions for 15
            [("+", 19), ("R", 5), ("G", 3)],  # reactions for 16
            [("-", 16), ("E", 8), ("C", 7)],  # reactions for 17
            [
                ("+", 3),
            ],  # reactions for 18
        ],
    },
]


def get_flat_list(a_list):
    flatten = []
    for item in a_list:
        if isinstance(item, tuple):
            flatten.extend(get_flat_list(item))
        else:
            flatten.append(item)
    return flatten


class Command(BaseCommand):
    help = "Add comments, reactions and votes to articles, stories and tales."
    _submit_date = None  # Changes for each comment added.
    _n_users = 0  # The number of users in the DB. For random selection.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._n_users = User.objects.count()
        self._submit_date = datetime(  # Initialize to January last year.
            datetime.now().year - 1,  # Year
            1,  # Month
            1,  # Day
            1,  # Hour
            randint(1, 59),  # Minute
            randint(1, 59),  # Second
            tzinfo=pytz.timezone(settings.TIME_ZONE),
        )

    def validate_content_parameters(self, item):
        """
        Validate entries in the items of `content_parameters`.

        Check that the number of elements in the `reactions` list,
        and the number of elements in the `votes` list does not
        exceed the number of comments.
        """
        if isinstance(item["comments"], int):
            assert len(item["reactions"]) <= item["comments"]
        if isinstance(item["comments"], list):
            flat_list = get_flat_list(item["comments"])
            assert len(item["reactions"]) <= len(flat_list)
        if len(item["reactions"]):
            for item_reactions in item["reactions"]:
                assert any(n == 0 for _, n in item_reactions) is False

    def get_submit_date(self):
        self._submit_date += timedelta(hours=1)
        return self._submit_date

    def add_comment(self, site, ctype, obj, reply_to=0):
        user = User.objects.get(pk=randint(1, self._n_users))
        return XtdComment.objects.create(
            content_type=ctype,
            object_pk=obj.id,
            content_object=obj,
            site=site,
            comment=lorem.sentence(),
            submit_date=self.get_submit_date(),
            user=user,
            parent_id=reply_to,
        )

    def add_comments_tuple(self, site, ctype, obj, tuple_item, reply_to=0):
        last_parent = None
        comments_added = []
        for elem in tuple_item:
            if isinstance(elem, int):
                last_parent = self.add_comment(site, ctype, obj, reply_to)
                comments_added.append(last_parent)
            elif isinstance(elem, tuple):  # It is last_parent's children.
                children = self.add_comments_tuple(
                    site, ctype, obj, elem, reply_to=last_parent.pk
                )
                comments_added.extend(children)
        return comments_added

    def add_reactions(self, comment, reactions_item):
        # A reactions_item may look like: [("+", 5), ("H", 2)]
        # It contains 2-item tuples. The 1st elem is the reaction, and
        # the 2nd element is the number of reactions to add. Each
        # from a different user.
        for reaction_value, reaction_count in reactions_item:
            c_reaction, created = CommentReaction.objects.get_or_create(
                reaction=reaction_value,
                comment=comment,
            )

            # If there were already authors for this reaction,
            # add only the missing number.
            n_existing_authors = c_reaction.authors.count()
            for _ in range(n_existing_authors, reaction_count):
                user_id = randint(1, self._n_users)
                user = User.objects.get(pk=user_id)
                c_reaction.authors.add(user)

            c_reaction.counter = reaction_count
            c_reaction.save()

    def handle(self, *args, **options):
        site = Site.objects.get(pk=1)
        comments_added = 0
        reactions_added = 0

        for item in content_parameters:
            # Before adding comments, reactions or votes,
            self.validate_content_parameters(item)
            ctype = ContentType.objects.get(
                app_label="prose",
                model=item["model"].lower(),
            )
            obj = ctype.model_class().objects.get(slug=item["slug"])

            comments = list(
                XtdComment.objects.filter(
                    content_type=ctype,
                    object_pk=obj.id,
                    site=site,
                )
            )
            # How many comments have received already the object?
            n_existing_comments = len(comments)

            if isinstance(item["comments"], int):
                # Add comments to the obj taking into account the number
                # of comments that already exists for the given object.
                for _ in range(n_existing_comments, item["comments"]):
                    comments.append(self.add_comment(site, ctype, obj))
                    comments_added += 1
            elif isinstance(item["comments"], list):
                # When the comments to add express a hierarchy (nested
                # comments), then each level 0 comment and its children
                # are given as a tuple.
                for ctuple in item["comments"]:
                    comments.extend(
                        self.add_comments_tuple(site, ctype, obj, ctuple)
                    )

            # Add reactions to each comment.
            for cidx, reactions_item in enumerate(item["reactions"]):
                # Each reactions_item is a list of tuples of two elements:
                # the reaction (see ReactionEnum, in mockups_project/enums.py)
                # and the number of reactions to create.
                self.add_reactions(comments[cidx], reactions_item)
                reactions_added += 1

        self.stdout.write("Done.")
