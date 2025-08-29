# ruff: noqa: N806
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.utils import ConnectionDoesNotExist

from django_comments_xtd.conf import settings
from django_comments_xtd.models import XtdComment


class Command(BaseCommand):
    help = "Initialize the nested_count field for all the comments in the DB."

    def add_arguments(self, parser):
        parser.add_argument("using", nargs="*", type=str)

    def initialize_nested_count(self, using):
        total_records = 0
        ctype_list = []

        # Check if the COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL is defined
        # and if so, iterate over each group of app_label.model, and apply
        # the update of the nested_count on per app_label.model group.
        # Then use the COMMENTS_XTD_MAX_THREAD_LEVEL to update the rest of
        # comments.

        # 1st: Process comments on per app_model basis.
        MTL_PER_APP = settings.COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL
        for app_model, mtl in MTL_PER_APP.items():
            bits = app_model.split(".")
            app, model = ".".join(bits[:-1]), bits[-1]
            try:
                ctype = ContentType.objects.get(app_label=app, model=model)
                ctype_list.append(ctype)
            except ContentType.DoesNotExist:
                self.stdout.write("app.model '%s' does not exist", app_model)
            else:
                qs = (
                    XtdComment.objects.using(using)
                    .filter(content_type=ctype, level__lte=mtl)
                    .order_by("thread__id", "-order")
                )
                count = self.process_queryset(qs)
                total_records += count
                self.stdout.write(
                    f"Updated {count} XtdComments for {app_model}."
                )

        # 2nd: Process the rest of the comments.
        MTL = settings.COMMENTS_XTD_MAX_THREAD_LEVEL
        if len(ctype_list) > 0:
            qs = (
                XtdComment.objects.using(using)
                .filter(~Q(content_type__in=ctype_list), level__lte=MTL)
                .order_by("thread__id", "-order")
            )
            count = self.process_queryset(qs)
            total_records += count
            self.stdout.write(f"Updated additional {count} XtdComments.")
        else:
            qs = (
                XtdComment.objects.using(using)
                .filter(level__lte=MTL)
                .order_by("thread__id", "-order")
            )
            total_records = self.process_queryset(qs)
            self.stdout.write(f"Updated {total_records} XtdComments.")

        return total_records

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
        self.stdout.write(f"Updated {total} XtdComment object(s).")
