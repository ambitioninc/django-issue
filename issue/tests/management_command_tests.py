from django.core.management import call_command
from django.test import TestCase

from mock import patch


class CheckAssertionsTests(TestCase):
    @patch('issue.check.check_assertions', spec_set=True)
    def test_check_assertions(self, check_assertions):
        call_command('check_assertions')
        self.assertTrue(check_assertions.called)


class RespondToIssuesTests(TestCase):
    @patch('issue.check.respond_to_issues', spec_set=True)
    def test_check_assertions(self, respond_to_issues):
        call_command('respond_to_issues')
        self.assertTrue(respond_to_issues.called)
