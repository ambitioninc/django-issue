from django.core.management.base import BaseCommand

from issue.check import respond_to_issues


class Command(BaseCommand):
    """
    Respond to any open issues.
    """
    def handle(self, *args, **options):
        respond_to_issues()
