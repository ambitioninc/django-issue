from django.contrib.contenttypes.models import ContentType

from issue.models import IssueAction, Issue


def normalize_generic_issues(apps, schema_editor):
    """
    Normalize related issues as generic reference
    """
    for issue_action in IssueAction.objects.all():
        issue_action.action_issue_type = ContentType.objects.get_for_model(Issue)
        issue_action.action_issue_id = issue_action.issue_id
        issue_action.save(update_fields=['action_issue_type', 'action_issue_id'])
