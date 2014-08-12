from datetime import datetime

from django.db import models
from django.utils.module_loading import import_by_path
from enum import Enum
from jsonfield import JSONField
from manager_utils import ManagerUtilsManager
from regex_field import RegexField


#######################################################
# Misc Utils
#######################################################
def load_function(dotted_path):
    return import_by_path(dotted_path)


class ExtendedEnum(Enum):
    @classmethod
    def name_to_value(cls, name):
        return getattr(cls, name).value

    @classmethod
    def choices(cls):
        return [(c.value, c.name) for c in list(cls)]


#######################################################
# Core Issue models
#######################################################
class IssueStatus(ExtendedEnum):
    """
    Enum listing possible Status values for an Issue.
    """
    Open = 0
    Resolved = 1
    Wont_fix = 2


class CommentType(ExtendedEnum):
    Note = 0
    Action = 1


class Note(models.Model):
    """
    Generic class for recording some event in the database.
    """
    name = models.TextField()
    details = JSONField(null=True, blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'Note: {name}'.format(name=self.name)


class IssueManager(ManagerUtilsManager):
    """
    Custom model manager for the Issue model.
    """
    def get_open_issues(self):
        """
        Retrive a queryset of all Open Issues.
        """
        return self.filter(status=IssueStatus.Open.value)


class Issue(Note):
    """
    Particular problems or issues that the system needs should keep a record of.
    """
    status = models.IntegerField(choices=IssueStatus.choices(), default=IssueStatus.Open.value)
    resolved_timestamp = models.DateTimeField(null=True, blank=True)

    objects = IssueManager()

    def __unicode__(self):
        return u'Issue: {name} - {status}'.format(name=self.name, status=IssueStatus(self.status))

    def add_comment(self, **kwargs):
        """
        Create an IssueComment refering to this Issue.
        """
        return IssueComment.objects.create(issue=self, **kwargs)


class IssueComment(Note):
    """
    A note about a particular issue.
    """
    issue = models.ForeignKey(Issue)
    comment_type = models.IntegerField(choices=CommentType.choices(), default=CommentType.Note.value)

    def __unicode__(self):
        return u'IssueComment: {issue.name} - {name}'.format(issue=self.issue, name=self.name)


#######################################################
# Issue Response models
#######################################################
class Responder(models.Model):
    """
    When an Issue is created, there is often an appropriate response.

    A Responder record encodes a particular type of Issue to watch for and what actions
    to take when an Issue is opened.

    Examples might be emailing an admin, opening a ticket in PagerDuty, or running a bit
    of code to fix a problem.

    The actions to be taken are implemented as ResponderActions that ForeignKey to a particular
    Responder record.
    """
    watch_pattern = RegexField(max_length=128)

    def __unicode__(self):
        return u'Responder: {watch_pattern.pattern}'.format(watch_pattern=self.watch_pattern)

    def respond(self, issue):
        """
        Check if the provided issue matches our watch pattern.

        If it does, execute the associated ResponderActions.
        """
        if self._match(issue.name):
            self._execute(issue)
            return True
        else:
            return False

    def _match(self, issue_name):
        return self.watch_pattern.match(issue_name)

    def _execute(self, issue):
        """
        Execute in order all of the ResponderActions associated with this Responder.
        """
        for a in self.actions.order_by('action_order'):
            if not a.execute(issue):
                return False
        else:
            return True


class ResponderAction(models.Model):
    """
    A particular action to take in response to some Issue.
    """
    responder = models.ForeignKey(Responder, related_name='actions')

    # What order this action should be taken in?
    action_order = models.IntegerField()

    # What action do we want to occur
    target_function = models.TextField()
    function_kwargs = JSONField(default={})

    def __unicode__(self):
        return u'ResponderAction: {responder} - {target_function} - {function_kwargs}'.format(
            responder=self.responder, target_function=self.target_function, function_kwargs=self.function_kwargs)

    def execute(self, issue):
        """
        Execute the configured action.
        """
        try:
            execution_successful = load_function(self.target_function)(issue, **self.function_kwargs)
            details = self.construct_details(execution_successful)
        except Exception as e:
            details = self.construct_details(False, str(e))

        issue.add_comment(details=details, comment_type=CommentType.Action.value)

        return details['ResponderAction']['success']

    def construct_details(self, success, failure_details=None):
        """
        Construct a summary of this action execution.
        """
        return {
            'ResponderAction': {
                'success': success,
                'execution_time': int(datetime.utcnow().strftime('%s')),
                'target_function': self.target_function,
                'failure_details': failure_details
            }
        }


#######################################################
# Assertion models
#######################################################
class Assertion(models.Model):
    """
    A class for tracking that certain properties of the web application are true.

    When an Assertion fails, an Issue is created to note this.

    Think of it as a cross between the classic 'assert' statement and a traditional software monitoring
    solution, like 'Nagios'.
    """
    # Class do we check to verify everything is copacetic?
    check_function = models.TextField()

    def check(self):
        """
        Run the configured check to detect problems and create or resolve issues as needed.
        """
        (all_is_well, issue_name, issue_details) = load_function(self.check_function)()

        if not all_is_well:
            self._open_issue(issue_name, issue_details)
        else:
            self._close_open_issue(issue_name)

        return all_is_well

    def _open_issue(self, name, details):
        """
        Open (or re-open) an issue with the name unless one exists with a status of Wont_fix.
        """
        if not Issue.objects.filter(name=name, status=IssueStatus.Wont_fix.value).exists():
            return Issue.objects.upsert(name=name, updates={
                'details': details,
                'status': IssueStatus.Open.value,
            })

    def _close_open_issue(self, issue_name):
        """
        Close any issues with this name.
        """
        Issue.objects.filter(name=issue_name).update(status=IssueStatus.Resolved.value)
