# ruff: noqa: PERF203
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import ConnectionDoesNotExist, IntegrityError
from django_comments.models import Comment

from django_comments_xtd.models import CommentThread, XtdComment

__all__ = ["Command"]


class Command(BaseCommand):
    help = "Load the xtdcomment table with valid data from django_comments."

    def add_arguments(self, parser):
        parser.add_argument("using", nargs="*", type=str)

    def populate_db(self, cursor):
        for comment in Comment.objects.all():
            #
            # Insert into django_comments_xtd_thread.
            sql = "INSERT INTO %(table)s ('id', 'score') VALUES (%(id)d, 0)"
            cursor.execute(
                sql % {"table": CommentThread._meta.db_table, "id": comment.id}
            )

            #
            # Insert into django_comments_ink_comment.
            sql = (
                "INSERT INTO %(table)s "
                "       ('comment_ptr_id', 'thread_id', 'parent_id',"
                "        'level', 'order', 'followup', 'nested_count') "
                "VALUES (%(id)d, %(id)d, %(id)d, 0, 1, FALSE, 0)"
            )
            cursor.execute(
                sql % {"table": XtdComment._meta.db_table, "id": comment.id}
            )

    def handle(self, *args, **options):
        total = 0
        using = options["using"] or ["default"]
        for db_conn in using:
            try:
                self.populate_db(connections[db_conn].cursor())
                total += XtdComment.objects.using(db_conn).count()
            except ConnectionDoesNotExist:
                self.stdout.write(f"DB connection '{db_conn}' does not exist.")
            except IntegrityError:
                if db_conn != "default":
                    self.stdout.write(
                        f"Table '{XtdComment._meta.db_table}' ("
                        f"in '{db_conn}' DB connection) must be empty."
                    )
                else:
                    self.stdout.write(
                        f"Table '{XtdComment._meta.db_table}' must be empty."
                    )
            finally:
                continue  # noqa: B012
        self.stdout.write(f"Added {total} XtdComment object(s).")
