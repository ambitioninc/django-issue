from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django_dynamic_fixture import G
from mock import call, patch

from issue.models import Assertion, Issue, ModelAssertion, ModelIssue, Responder
from issue.check import check_assertions, respond_to_issues


class CheckAssertionsTests(TestCase):
    @patch.object(ModelAssertion, 'check_assertion', spec_set=True, return_value=False)
    @patch.object(Assertion, 'check_assertion', spec_set=True, return_value=False)
    def test_check_assertions_checks_assertions_and_model_assertions(self, assertion_check, model_assertion_check):
        # Setup the scenario
        Assertion.objects.create(name='an-assertion')
        ModelAssertion.objects.create(name='a-model-assertion', model_type=ContentType.objects.get_for_model(Issue))

        # Run the code
        failing_assertion_count = check_assertions()

        # Verify expectations
        self.assertEqual(2, failing_assertion_count)
        self.assertTrue(assertion_check.called)
        self.assertTrue(model_assertion_check.called)

    @patch.object(Assertion, 'check_assertion', spec_set=True, side_effect=[True, False])
    def test_check_assertions_counts_only_failing(self, assertion_check):
        # Setup the scenario
        Assertion.objects.create(name='an-assertion')
        Assertion.objects.create(name='another-assertion')

        # Run the code
        failing_assertion_count = check_assertions()

        # Verify expectations
        self.assertEqual(1, failing_assertion_count)
        self.assertTrue(assertion_check.called)


class RespondToIssuesTests(TestCase):
    @patch.object(Responder, 'respond', spec_set=True)
    def test_respond_to_issues_checks_issues_and_model_issues(self, respond):
        # Setup the scenario
        i = Issue.objects.create(name='an-issue')
        am1 = G(Assertion, name='1')
        mi = ModelIssue.objects.create(record_id=am1.id, record_type=ContentType.objects.get_for_model(Issue))
        G(Responder)

        # Run the code
        respond_to_issues()

        # Verify expectations
        respond.assert_has_calls([call(i), call(mi)], any_order=True)
