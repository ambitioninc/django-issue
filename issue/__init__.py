# flake8: noqa
from .version import __version__
from .models import Assertion, Issue, IssueManager, IssueStatus, ModelAssertion, ModelIssue, ModelIssueManager, Responder, ResponderAction

django_app_config = 'issue.apps.IssueConfig'
