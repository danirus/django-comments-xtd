from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import ConnectionDoesNotExist, IntegrityError
from django_comments.models import Comment

from django_comments_xtd.models import XtdComment

__all__ = ["Command"]


class Command(BaseCommand):
    help = "Load the xtdcomment table with valid data from django_comments."

    def add_arguments(self, parser):
        parser.add_argument("using", nargs="*", type=str)

    def populate_db(self, cursor):
        for comment in Comment.objects.all():
            sql = (
                "INSERT INTO %(table)s "
                "       ('comment_ptr_id', 'thread_id', 'parent_id',"
                "        'level', 'order', 'followup') "
                "VALUES (%(id)d, %(id)d, %(id)d, 0, 1, FALSE)"
            )
            cursor.execute(
                sql % {"table": XtdComment._meta.db_table, "id": comment.id}
            )

    def handle(self, *args, **options):
        total = 0
        using = options["using"] or ["default"]
        try:
            for db_conn in using:
                self.populate_db(connections[db_conn].cursor())
                total += XtdComment.objects.using(db_conn).count()
        except ConnectionDoesNotExist:
            self.stdout.write(f"DB connection '{db_conn}' does not exist.")
        except IntegrityError:
            if db_conn != "default":
                self.stdout.write(
                    f"Table '{XtdComment._meta.db_table}' "
                    f"(in '{db_conn}' DB connection) must be empty."
                )
            else:
                self.stdout.write(
                    f"Table '{XtdComment._meta.db_table}' must be empty."
                )
        self.stdout.write(f"Added {total} XtdComment object(s).")
