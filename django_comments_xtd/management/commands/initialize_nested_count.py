from django.db.utils import ConnectionDoesNotExist
from django.core.management.base import BaseCommand

from django_comments_xtd.models import XtdComment


class Command(BaseCommand):
    help = "Initialize the nested_count field for all the comments in the DB."

    def add_arguments(self, parser):
        parser.add_argument('using', nargs='*', type=str)

    def initialize_nested_count(self, using):
        # Control break.
        active_thread_id = -1
        parents = {}

        qs = XtdComment.objects.using(using).order_by('thread_id', '-order')

        for comment in qs:
            # Clean up parents when there is a control break.
            if comment.thread_id != active_thread_id:
                parents = {}
                active_thread_id = comment.thread_id

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
        using = options['using'] or ['default']

        for db_conn in using:
            try:
                total += self.initialize_nested_count(db_conn)
            except ConnectionDoesNotExist:
                self.stdout.write("DB connection '%s' does not exist." %
                                  db_conn)
                continue
        self.stdout.write("Updated %d XtdComment object(s)." % total)
