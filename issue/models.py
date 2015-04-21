from copy import copy
from datetime import datetime, timedelta
import json

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.module_loading import import_by_path
from enum import Enum
from jsonfield import JSONField
from manager_utils import ManagerUtilsManager
from regex_field import RegexField


#######################################################
# Misc Utils
#######################################################
import six


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


class IssueManager(ManagerUtilsManager):
    """
    Custom model manager for the Issue model.
    """
    def get_open_issues(self):
        """
        Retrive a queryset of all Open Issues.
        """
        return self.filter(status=IssueStatus.Open.value)

    def reopen_issue(self, name, **kwargs):
        """
        Reopen the specified Issue.
        """
        kwargs['status'] = IssueStatus.Open.value
        self.filter(name=name).update(**kwargs)

    def is_wont_fix(self, **kwargs):
        """
        Does the specified issue exist with a status of Wont_fix?
        """
        return self.filter(status=IssueStatus.Wont_fix.value, **kwargs).exists()

    def resolve_issue(self, **kwargs):
        """
        Resolve the specified issue.
        """
        self.filter(**kwargs).update(status=IssueStatus.Resolved.value)

    def maybe_open_issue(self, name, **kwargs):
        """
        Create the specified Issue unless:
        1) It is already open - if so, return it
        2) It already exists and is marked as Wont_fix

        Returns a tuple (Issue, Boolean) containing the Issue and if it was created.
        """
        if self.filter(name=name, status=IssueStatus.Wont_fix.value).exists():
            # Exists but is Wont_fix
            return None, False

        if self.filter(name=name, status=IssueStatus.Open.value).exists():
            # Exists and is Open
            return self.filter(name=name, status=IssueStatus.Open.value).latest('creation_time'), False

        # Either an Issue of this name doesn't exist or it is Resolved; either way, create one!
        return self.create(name=name, **kwargs), True


@six.python_2_unicode_compatible
class BaseIssue(models.Model):
    name = models.TextField()
    details = JSONField(null=True, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=IssueStatus.choices(), default=IssueStatus.Open.value)
    resolved_time = models.DateTimeField(null=True, blank=True)

    objects = IssueManager()

    class Meta:
        abstract = True

    def __str__(self):
        return 'Issue: {name} - {status}'.format(name=self.name, status=IssueStatus(self.status))

    @property
    def is_open(self):
        return self.status == IssueStatus.Open.value

    @property
    def is_resolved(self):
        return self.status == IssueStatus.Resolved.value

    @property
    def is_wont_fix(self):
        return self.status == IssueStatus.Wont_fix.value


class ModelIssueManager(IssueManager):
    def _replace_record_with_content_type(self, kwargs):
        kwargs = copy(kwargs)
        record = kwargs.pop('record', None)

        if record:
            kwargs['record_id'], kwargs['record_type'] = (
                record.id, ContentType.objects.get_for_model(record)
            )

        return kwargs

    def reopen_issue(self, *args, **kwargs):
        """
        Reopen the specified Issue.
        """
        kwargs = self._replace_record_with_content_type(kwargs)

        return super(ModelIssueManager, self).reopen_issue(*args, **kwargs)

    def is_wont_fix(self, *args, **kwargs):
        """
        Does the specified issue exist with a status of Wont_fix?
        """
        kwargs = self._replace_record_with_content_type(kwargs)

        return super(ModelIssueManager, self).is_wont_fix(*args, **kwargs)

    def resolve_issue(self, *args, **kwargs):
        """
        Resolve the specified issue.
        """
        kwargs = self._replace_record_with_content_type(kwargs)

        return super(ModelIssueManager, self).resolve_issue(*args, **kwargs)


class Issue(BaseIssue):
    """
    Particular problems or issues that the system needs should keep a record of.
    """
    pass


class ModelIssue(BaseIssue):
    """
    An issue involving a particular entry in the database.
    """
    record_type = models.ForeignKey(ContentType, related_name='+', null=True)
    record_id = models.PositiveIntegerField(default=0)
    record = generic.GenericForeignKey('record_type', 'record_id')

    objects = ModelIssueManager()


@six.python_2_unicode_compatible
class IssueAction(models.Model):
    """
    A response that was taken to address a particular issue.
    """
    issue = models.ForeignKey(Issue, related_name='executed_actions')
    responder_action = models.ForeignKey('issue.ResponderAction')
    execution_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    details = JSONField(null=True, blank=True)

    def __str__(self):
        return (
            'IssueResponse: {self.issue.name} - {self.responder_action} - '
            '{self.success} at {self.execution_time}'.format(self=self)
        )


#######################################################
# Issue Response models
#######################################################
@six.python_2_unicode_compatible
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
    watch_pattern = RegexField(null=True, max_length=128)

    def __str__(self):
        return 'Responder: {watch_pattern.pattern}'.format(watch_pattern=self.watch_pattern)

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
        IssueAction.objects.bulk_create(
            [
                a.execute(issue) for a in self._get_pending_actions_for_issue(issue)
                if a.is_time_to_execute(issue)
            ])

    def _get_pending_actions_for_issue(self, issue):
        already_executed_action_pks = issue.executed_actions.values_list('responder_action__pk', flat=True).all()

        return self.actions.exclude(pk__in=already_executed_action_pks).order_by('delay_sec')


@six.python_2_unicode_compatible
class ResponderAction(models.Model):
    """
    A particular action to take in response to some Issue.

    Any function can be specified in the target_function field, though some initial
    helpers are defined in issue.actions
    """
    responder = models.ForeignKey(Responder, related_name='actions')

    # 'buffer' period between this action and the next.
    delay_sec = models.IntegerField()

    # What action do we want to occur
    target_function = models.TextField()
    function_kwargs = JSONField(default={})

    def __str__(self):
        return 'ResponderAction: {responder} - {target_function} - {function_kwargs}'.format(
            responder=self.responder, target_function=self.target_function, function_kwargs=self.function_kwargs)

    @property
    def delay(self):
        return timedelta(seconds=self.delay_sec)

    def is_time_to_execute(self, issue):
        """
        A ResponseAction is only executable if enough time has passed since the previous action.
        """
        return (issue.creation_time + self.delay) <= datetime.utcnow()

    def execute(self, issue):
        """
        Execute the configured action.
        """
        try:
            details = load_function(self.target_function)(issue, **self.function_kwargs)
            kwargs = self.construct_issue_action_kwargs(True, details)
        except Exception as e:
            kwargs = self.construct_issue_action_kwargs(False, str(e))

        return IssueAction(issue=issue, **kwargs)

    def construct_issue_action_kwargs(self, success, failure_details=None):
        """
        Construct a summary of this action execution.
        """
        return {
            'responder_action': self,
            'execution_time': str(datetime.utcnow()),
            'success': success,
            'details': json.dumps(failure_details),
        }


#######################################################
# Assertion models
#######################################################
class BaseAssertion(models.Model):
    """
    A class for tracking that certain properties of the web application are true.

    When an Assertion fails, an Issue is created to note this.

    Think of it as a cross between the classic 'assert' statement and a traditional software monitoring
    solution, like 'Nagios'.
    """
    # Class do we check to verify everything is copacetic?
    check_function = models.TextField()

    # Assertion name; also the name of any Issue created
    name = models.TextField()

    class Meta:
        abstract = True

    @property
    def issue_class(self):
        return Issue

    def check_assertion(self, *args, **kwargs):
        """
        Run the configured check to detect problems and create or resolve issues as needed.
        """
        (all_is_well, details) = load_function(self.check_function)(**kwargs)

        if not all_is_well:
            kwargs['details'] = details
            self._open_or_update_issue(**kwargs)
        else:
            self._resolve_open_issue(**kwargs)

        return all_is_well

    def _open_or_update_issue(self, details, **kwargs):
        """
        Open (or re-open) an issue with the name unless one exists with a status of Wont_fix.
        """
        return self.issue_class.objects.maybe_open_issue(self.name, **kwargs)[0]

    def _resolve_open_issue(self, **kwargs):
        """
        Resolve any issues with this name.
        """
        self.issue_class.objects.resolve_issue(name=self.name, **kwargs)


class Assertion(BaseAssertion):
    pass


class ModelAssertion(BaseAssertion):
    """
    A class for making assertions about models.

    An Issue is created for any record for which the assertion fails.
    """
    model_type = models.ForeignKey(ContentType, related_name='+')

    @property
    def issue_class(self):
        return ModelIssue

    @property
    def queryset(self):
        """
        Queryset of records to iterate over.
        """
        return self.model_type.model_class().objects.all()

    def check_assertion(self, **kwargs):
        """
        Run the configured check against all records in the queryset to detect problems.

        Returns True if the assertion holds true for all records of the configured model type.
        """
        def check_record(record):
            return super(ModelAssertion, self).check_assertion(record=record, **kwargs)

        return all(map(check_record, self.queryset))
