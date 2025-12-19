# ruff: noqa: N806
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.utils import ConnectionDoesNotExist

from django_comments_xtd import utils
from django_comments_xtd.conf import settings
from django_comments_xtd.models import XtdComment


class Command(BaseCommand):
    help = "Initialize the nested_count field for all the comments in the DB."

    def add_arguments(self, parser):
        parser.add_argument("using", nargs="*", type=str)

    def initialize_nested_count(self, using):
        total = 0
        ctype_list = []

        # Check if the `max_thread_level` is provided for each app_model
        # given in COMMENTS_XTD_APP_MODEL_CONFIG, and if so, iterate over
        # each app_model, read the max_thread_level and apply the update
        # of the nested_count on per app_model group.
        # Then use the COMMENTS_XTD_DEFAULT_MAX_THREAD_LEVEL to update
        # the rest of comments.

        # 1st: Process comments on per app_model basis.
        for app_model in settings.COMMENTS_XTD_APP_MODEL_CONFIG:
            if app_model == "default":
                continue

            bits = app_model.split(".")
            app, model = ".".join(bits[:-1]), bits[-1]
            try:
                ctype = ContentType.objects.get(app_label=app, model=model)
                ctype_list.append(ctype)
            except ContentType.DoesNotExist:
                self.stderr.write(
                    f"app.model '{app_model}' listed in "
                    "COMMENTS_XTD_APP_MODEL_CONFIG does not exist "
                    "as a ContentType instance."
                )
            else:
                mtl = utils.get_max_thread_level(ctype)
                qs = (
                    XtdComment.objects.using(using)
                    .filter(content_type=ctype, level__lte=mtl)
                    .order_by("thread__id", "-order")
                )
                count = self.process_queryset(qs)
                total += count
                self.stdout.write(
                    f"Updated {count} XtdComments for {app_model}."
                )

        # 2nd: Process the rest of the comments.
        MTL = settings.COMMENTS_XTD_DEFAULT_MAX_THREAD_LEVEL
        if len(ctype_list) > 0:
            # Process those comments posted to content_types
            # not included in the ctype_list.
            #
            qs = (
                XtdComment.objects.using(using)
                .filter(~Q(content_type__in=ctype_list), level__lte=MTL)
                .order_by("thread__id", "-order")
            )
            count = self.process_queryset(qs)
            total += count
            self.stdout.write(f"Updated additional {count} XtdComments.")
        else:
            # Process all comments as no explicit content_type
            # has been processed yet.
            qs = (
                XtdComment.objects.using(using)
                .filter(level__lte=MTL)
                .order_by("thread__id", "-order")
            )
            total = self.process_queryset(qs)
            self.stdout.write(f"Updated {total} XtdComments.")

        return total

    def process_queryset(self, qs):
        active_thread_id = -1
        parents = {}

        for comment in qs:
            # Clean up parents when there is a control break.
            if comment.thread.id != active_thread_id:
                parents = {}
                active_thread_id = comment.thread.id

            nested_count = parents.get(comment.comment_ptr_id, 0)
            parents.setdefault(comment.parent_id, 0)
            if nested_count > 0:
                parents[comment.parent_id] += 1 + nested_count
            else:
                parents[comment.parent_id] += 1
            comment.nested_count = nested_count
            comment.save()

        return qs.count()

    def handle(self, *args, **options):
        total = 0
        using = options["using"] or ["default"]

        try:
            for db_conn in using:
                total += self.initialize_nested_count(db_conn)
        except ConnectionDoesNotExist:
            self.stdout.write(f"DB connection '{db_conn}' does not exist.")
        else:
            self.stdout.write(f"Updated {total} XtdComment object(s).")
