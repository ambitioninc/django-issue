from django.core.management.base import BaseCommand

from issue.check import check_assertions


class Command(BaseCommand):
    """
    Check all assertions to see if they are true.
    """
    def handle(self, *args, **options):
        check_assertions()
