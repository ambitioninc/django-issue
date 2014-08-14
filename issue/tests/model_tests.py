from datetime import datetime, timedelta

from django.test import TestCase
from django_dynamic_fixture import G, N
from freezegun import freeze_time
from mock import patch

from issue.models import (
    Assertion, ExtendedEnum, Issue, IssueAction, IssueStatus, Responder, ResponderAction,
    load_function,
)


def function_to_load(self, *args, **kwargs):
    pass


class LoadFucntionTests(TestCase):
    def test_load_class_instance(self):
        func = load_function('issue.tests.model_tests.function_to_load')
        self.assertEqual(func, function_to_load)


class ExtendedEnumTests(TestCase):
    class TestEnum(ExtendedEnum):
        red = 1
        blue = 3
        green = 2

    def test_name_to_value(self):
        self.assertEqual(2, ExtendedEnumTests.TestEnum.name_to_value('green'))

    def test_choices(self):
        self.assertEqual(
            set([(1, 'red'), (2, 'green'), (3, 'blue')]), set(ExtendedEnumTests.TestEnum.choices()))


class IssueManagerTests(TestCase):
    def test_get_open_issues(self):
        i = G(Issue)
        G(Issue, status=IssueStatus.Resolved.value)
        i3 = G(Issue)
        self.assertEqual(set(Issue.objects.get_open_issues()), set([i, i3]))


class IssueTests(TestCase):
    def test__unicode__(self):
        i = Issue(name='an-issue', status=IssueStatus.Resolved.value)
        self.assertEqual('Issue: an-issue - IssueStatus.Resolved', i.__unicode__())


class IssueActionTests(TestCase):
    def test__unicode__(self):
        ia = N(IssueAction)
        self.assertEqual(
            u'IssueResponse: {self.issue.name} - {self.responder_action} - '
            '{self.success} at {self.execution_time}'.format(self=ia),
            ia.__unicode__())


class ResponderTests(TestCase):
    def test__unicode__(self):
        self.assertEqual('Responder: error-.*', Responder(watch_pattern='error-.*').__unicode__())

    @patch('issue.models.load_function', spec_set=True)
    def test_respond(self, load_function):
        # Setup the scenario
        target_function = 'do'
        issue = G(Issue, name='error-42')
        responder = G(Responder, issue=issue, watch_pattern='error-\d+')
        G(ResponderAction, responder=responder, target_function=target_function, delay_sec=0)

        # Run the code
        r = responder.respond(issue)

        # Verify expectations
        self.assertTrue(r)
        load_function.assert_called_with(target_function)

    @patch('issue.models.load_function', spec_set=True)
    def test_respond_ignores_non_watching_pattern(self, load_function):
        # Setup the scenario
        issue = G(Issue, name='success')
        responder = G(Responder, issue=issue, watch_pattern='error-\d+')
        G(ResponderAction, responder=responder, target_function='do')

        # Run the code
        r = responder.respond(issue)

        # Verify expectations
        self.assertFalse(r)
        self.assertFalse(load_function.called)

    def test__match(self):
        r = Responder(watch_pattern='error-.*')
        self.assertTrue(r._match('error-42'))
        self.assertFalse(r._match('success'))

    @patch('issue.models.load_function', spec_set=True)
    def test__execute_all_success(self, load_function):
        # Setup the scenario
        issue = G(Issue)
        responder = G(Responder, issue=issue)
        # Note: we don't care what the target_function path is since we patch the load_function function
        ra = G(ResponderAction, responder=responder, delay_sec=0)
        ra2 = G(ResponderAction, responder=responder, delay_sec=0)
        ra3 = G(ResponderAction, responder=responder, delay_sec=0)

        self.do_call_time = None
        self.do_2_call_time = None
        self.do_3_call_time = None

        def do_1(*args, **kwargs):
            self.do_call_time = datetime.utcnow()
            return True

        def do_2(*args, **kwargs):
            self.do_2_call_time = datetime.utcnow()
            return True

        def do_3(*args, **kwargs):
            self.do_3_call_time = datetime.utcnow()
            return True

        load_function.side_effect = [do_1, do_2, do_3]

        # Run the code
        responder._execute(issue)

        # Verify expectations
        self.assertTrue(self.do_call_time < self.do_2_call_time)
        self.assertTrue(self.do_2_call_time < self.do_3_call_time)

        self.assertTrue(IssueAction.objects.filter(issue=issue, responder_action=ra).exists())
        self.assertTrue(IssueAction.objects.filter(issue=issue, responder_action=ra2).exists())
        self.assertTrue(IssueAction.objects.filter(issue=issue, responder_action=ra3).exists())

    @patch('issue.models.load_function', spec_set=True)
    def test__execute_stops_when_some_actions_are_not_yet_executable(self, load_function):
        # Setup the scenario
        delta = timedelta(seconds=30)
        issue = G(Issue, creation_time=datetime.utcnow() - (2 * delta))
        responder = G(Responder, issue=issue)
        ra = G(ResponderAction, responder=responder, delay_sec=0, target_function='do_1')
        ra2 = G(ResponderAction, responder=responder, delay_sec=0, target_function='do_2')
        ra3 = G(ResponderAction, responder=responder, delay_sec=30, target_function='do_3')

        self.do_call_time = None
        self.do_2_call_time = None
        self.do_3_call_time = None

        def do_1(*args, **kwargs):
            self.do_call_time = datetime.utcnow()
            return True

        def do_2(*args, **kwargs):
            self.do_2_call_time = datetime.utcnow()
            return True

        def do_3(*args, **kwargs):
            self.do_3_call_time = datetime.utcnow()
            return True

        load_function.side_effect = lambda tf: {'do_1': do_1, 'do_2': do_2}[tf]

        # Run the code
        responder._execute(issue)

        # Verify expectations
        self.assertTrue(self.do_call_time < self.do_2_call_time)
        self.assertIsNone(self.do_3_call_time)

        self.assertTrue(IssueAction.objects.filter(issue=issue, responder_action=ra).exists())
        self.assertTrue(IssueAction.objects.filter(issue=issue, responder_action=ra2).exists())
        self.assertTrue(IssueAction.objects.filter(issue=issue, responder_action=ra3).exists())

    @freeze_time(datetime(2014, 8, 13, 12))
    @patch('issue.models.load_function', spec_set=True)
    def test__execute_resumes_after_sufficient_time(self, load_function):
        # Setup the scenario
        delta = timedelta(seconds=30)
        issue = G(Issue, creation_time=datetime.utcnow() - (2 * delta))
        responder = G(Responder, issue=issue)
        ra = G(ResponderAction, responder=responder, delay_sec=0, target_function='do_1')
        ra2 = G(ResponderAction, responder=responder, delay_sec=delta.total_seconds(), target_function='do_2')
        G(IssueAction, issue=issue, responder_action=ra)

        self.do_called = False
        self.do_2_called = False

        def do_1(*args, **kwargs):
            self.do_called = True
            return True

        def do_2(*args, **kwargs):
            self.do_2_called = True
            return True

        load_function.side_effect = lambda tf: {'do_1': do_1, 'do_2': do_2}[tf]

        # Run the code
        responder._execute(issue)

        # Verify expectations
        self.assertFalse(self.do_called)
        self.assertTrue(self.do_2_called)

        self.assertTrue(IssueAction.objects.filter(issue=issue, responder_action=ra).exists())
        self.assertTrue(IssueAction.objects.filter(issue=issue, responder_action=ra2).exists())

    @patch('issue.models.load_function', spec_set=True)
    def test__execute_failure_does_not_stop_other_actions(self, load_function):
        # Setup the scenario
        delta = timedelta(seconds=30)
        issue = G(Issue, creation_time=datetime.utcnow() - (2 * delta))
        responder = G(Responder, issue=issue)
        # Note: we don't care what the target_function path is since we patch the load_function function
        ra = G(ResponderAction, responder=responder, delay_sec=0)
        ra2 = G(ResponderAction, responder=responder, delay_sec=0)
        ra3 = G(ResponderAction, responder=responder, delay_sec=30)

        self.do_call_time = None
        self.do_2_call_time = None
        self.do_3_call_time = None

        def do_1(*args, **kwargs):
            self.do_call_time = datetime.utcnow()
            return None

        def do_2(*args, **kwargs):
            self.do_2_call_time = datetime.utcnow()
            raise Exception('what-an-exceptional-message')

        def do_3(*args, **kwargs):
            self.do_3_call_time = datetime.utcnow()
            return None

        load_function.side_effect = [do_1, do_2, do_3]

        # Run the code
        responder._execute(issue)

        # Verify expectations
        self.assertTrue(self.do_call_time < self.do_2_call_time)
        self.assertTrue(self.do_2_call_time < self.do_3_call_time)

        self.assertTrue(IssueAction.objects.filter(issue=issue, responder_action=ra).exists())
        self.assertTrue(IssueAction.objects.filter(issue=issue, responder_action=ra2).exists())
        self.assertTrue(IssueAction.objects.filter(issue=issue, responder_action=ra3).exists())
        self.assertEqual(
            str(Exception('what-an-exceptional-message')),
            IssueAction.objects.get(issue=issue, responder_action=ra2).details)


class ResponderActionTests(TestCase):
    def test__unicode(self):
        r = G(ResponderAction)
        self.assertEqual(
            'ResponderAction: {responder} - {target_function} - {function_kwargs}'.format(
                responder=r.responder, target_function=r.target_function, function_kwargs=r.function_kwargs),
            r.__unicode__())

    def test_is_time_to_execute(self):
        # Setup the scenario
        now = datetime(2014, 8, 11, 15, 0, 0)
        delta = timedelta(minutes=30)
        ra = G(ResponderAction, delay_sec=delta.total_seconds())

        # Run the code and verify expectation
        issue = N(Issue, creation_time=now - (delta * 2))
        with freeze_time(now):
            self.assertTrue(ra.is_time_to_execute(issue))

    def test_is_time_to_execute_when_not_enough_time_has_passed(self):
        # Setup the scenario
        now = datetime(2014, 8, 11, 15, 0, 0)
        delta = timedelta(minutes=30)
        ra = G(ResponderAction, delay_sec=delta.total_seconds())

        # Run the code and verify expectation
        issue = N(Issue, creation_time=now - (delta / 2))
        with freeze_time(now):
            self.assertFalse(ra.is_time_to_execute(issue))

    @patch('issue.models.load_function', spec_set=True)
    def test_execute(self, load_function):
        # Setup the scenario
        target_function = 'do'
        issue = G(Issue)
        r = G(ResponderAction, target_function=target_function, function_kwargs={'foo': 'bar'})
        now = datetime(2014, 8, 11, 15, 0, 0)

        self.assertEqual(0, IssueAction.objects.count())
        load_function.return_value.return_value = None

        # Run the code
        with freeze_time(now):
            ia = r.execute(issue)
            ia.save()
            self.assertTrue(isinstance(ia, IssueAction))

        # Verify expectations
        expected_issue_action_kwargs = {
            'success': True,
            'execution_time': now,
            'responder_action': r,
        }
        load_function.assert_called_with(target_function)
        load_function.return_value.assert_called_with(issue, foo='bar')

        self.assertTrue(IssueAction.objects.filter(issue=issue, **expected_issue_action_kwargs).exists())
        self.assertIsNone(IssueAction.objects.get().details)

    @patch('issue.models.load_function', spec_set=True)
    def test_execute_with_failure(self, load_function):
        # Setup the scenario
        target_function = 'fail'
        issue = G(Issue)
        r = G(ResponderAction, target_function=target_function, function_kwargs={'foo': 'bar'})
        now = datetime(2014, 8, 11, 15, 0, 0)

        self.assertEqual(0, IssueAction.objects.count())
        load_function.return_value.side_effect = Exception('what-an-exceptional-message')

        # Run the code
        with freeze_time(now):
            ia = r.execute(issue)
            ia.save()
            self.assertTrue(isinstance(ia, IssueAction))

        # Verify expectations
        expected_issue_action_kwargs = {
            'success': False,
            'execution_time': now,
            'responder_action': r,
        }
        load_function.assert_called_with(target_function)
        load_function.return_value.assert_called_with(issue, foo='bar')

        self.assertTrue(IssueAction.objects.filter(issue=issue, **expected_issue_action_kwargs).exists())
        self.assertEqual(str(Exception('what-an-exceptional-message')), IssueAction.objects.get().details)


class AssertionTests(TestCase):
    @patch.object(Assertion, '_close_open_issue', spec_set=True)
    @patch('issue.models.load_function', spec_set=True)
    def test_check_when_all_is_well(self, load_function, close_open_issue):
        issue_name = 'an-issue'
        issue_details = {
            'narg': 'baz',
        }
        load_function.return_value.return_value = (True, issue_name, issue_details)

        assertion = G(Assertion, check_function='issue.tests.model_tests.load_function')

        self.assertTrue(assertion.check())
        close_open_issue.assert_called_with(issue_name)

    @patch.object(Assertion, '_open_issue', spec_set=True)
    @patch('issue.models.load_function', spec_set=True)
    def test_check_when_all_is_not_well(self, load_function, open_issue):
        issue_name = 'an-issue'
        issue_details = {
            'narg': 'baz',
        }
        load_function.return_value.return_value = (False, issue_name, issue_details)

        assertion = G(Assertion, check_function='issue.tests.model_tests.load_function')

        self.assertFalse(assertion.check())
        open_issue.assert_called_with(issue_name, issue_details)

    def test__open_issue_when_none_exists(self):
        issue_name = 'an-issue'
        Assertion()._open_issue(issue_name, {})
        self.assertEqual(IssueStatus.Open.value, Issue.objects.get(name=issue_name).status)

    def test__open_issue_when_it_is_marked_as_wont_fix(self):
        issue = G(Issue, status=IssueStatus.Wont_fix.value)
        Assertion()._open_issue(issue.name, {})
        self.assertEqual(IssueStatus.Wont_fix.value, Issue.objects.get(pk=issue.pk).status)

    def test__open_issue_when_it_is_marked_as_resolved(self):
        issue = G(Issue, status=IssueStatus.Resolved.value)
        Assertion()._open_issue(issue.name, {})
        self.assertEqual(IssueStatus.Open.value, Issue.objects.get(pk=issue.pk).status)

    def test_close_open_issue(self):
        issue = G(Issue, status=IssueStatus.Open.value)
        Assertion()._close_open_issue(issue.name)
        self.assertEqual(IssueStatus.Resolved.value, Issue.objects.get(pk=issue.pk).status)
