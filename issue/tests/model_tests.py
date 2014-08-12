from datetime import datetime

from django.test import TestCase
from django_dynamic_fixture import G, N
from freezegun import freeze_time
from mock import patch

from issue.models import (
    Assertion, ExtendedEnum, CommentType, Issue, IssueComment, IssueStatus, Note, Responder, ResponderAction,
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
        self.assertEqual([(1, 'red'), (2, 'green'), (3, 'blue')], ExtendedEnumTests.TestEnum.choices())


class NoteTests(TestCase):
    def test__unicode(self):
        self.assertEqual('Note: happy-note', Note(name='happy-note').__unicode__())


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

    def test_add_comment(self):
        i = G(Issue)
        comment_1_name = 'a-comment'
        comment_1_details = {
            'foo': 'bar',
        }
        comment_2_name = 'another-comment'

        i.add_comment(name=comment_1_name, details=comment_1_details)
        i.add_comment(name=comment_2_name, comment_type=CommentType.Action.value)

        self.assertEqual(
            comment_1_details,
            IssueComment.objects.get(issue=i, name=comment_1_name).details)
        self.assertTrue(
            IssueComment.objects.filter(issue=i, name=comment_2_name, comment_type=CommentType.Action.value).exists())


class IssueCommentTests(TestCase):
    def test__unicode__(self):
        ic = IssueComment(name='a-comment-name', issue=N(Issue, name='an-issue-name'))
        self.assertEqual('IssueComment: an-issue-name - a-comment-name', ic.__unicode__())


class ResponderTests(TestCase):
    def test__unicode__(self):
        self.assertEqual('Responder: error-.*', Responder(watch_pattern='error-.*').__unicode__())

    @patch.object(ResponderAction, 'execute', spec_set=True)
    def test_respond(self, execute):
        # Setup the scenario
        issue = G(Issue, name='error-42')
        responder = G(Responder, issue=issue, watch_pattern='error-\d+')
        G(ResponderAction, responder=responder, target_function='do')

        # Run the code
        r = responder.respond(issue)

        # Verify expectations
        self.assertTrue(r)
        execute.assert_called_with(issue)

    @patch.object(ResponderAction, 'execute', spec_set=True)
    def test_respond_ignores_non_watching_pattern(self, execute):
        # Setup the scenario
        issue = G(Issue, name='success')
        responder = G(Responder, issue=issue, watch_pattern='error-\d+')
        G(ResponderAction, responder=responder, target_function='do')

        # Run the code
        r = responder.respond(issue)

        # Verify expectations
        self.assertFalse(r)
        self.assertFalse(execute.called)

    def test__match(self):
        r = Responder(watch_pattern='error-.*')
        self.assertTrue(r._match('error-42'))
        self.assertFalse(r._match('success'))

    @patch('issue.models.load_function', spec_set=True)
    def test__execute_all_success(self, load_function):
        # Setup the scenario
        issue = G(Issue)
        responder = G(Responder, issue=issue)
        G(ResponderAction, responder=responder, action_order=1, target_function='made.up.path')
        G(ResponderAction, responder=responder, action_order=2, target_function='made.up.path2')
        G(ResponderAction, responder=responder, action_order=0, target_function='made.up.path3')

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
        r = responder._execute(issue)

        # Verify expectations
        self.assertTrue(r)
        self.assertTrue(self.do_call_time < self.do_2_call_time)
        self.assertTrue(self.do_2_call_time < self.do_3_call_time)

    @patch('issue.models.load_function', spec_set=True)
    def test__execute_failure(self, load_function):
        # Setup the scenario
        issue = G(Issue)
        responder = G(Responder, issue=issue)
        G(ResponderAction, responder=responder, action_order=0, target_function='made.up.path')
        G(ResponderAction, responder=responder, action_order=1, target_function='made.up.path2')
        G(ResponderAction, responder=responder, action_order=2, target_function='made.up.path3')

        self.do_call_time = None
        self.do_2_call_time = None
        self.do_3_call_time = None

        def do_1(*args, **kwargs):
            self.do_call_time = datetime.utcnow()
            return True

        def do_2(*args, **kwargs):
            self.do_2_call_time = datetime.utcnow()
            raise Exception('what-an-exceptional-message')

        def do_3(*args, **kwargs):
            self.do_3_call_time = datetime.utcnow()
            return True

        load_function.side_effect = [do_1, do_2, do_3]

        # Run the code
        r = responder._execute(issue)

        # Verify expectations
        self.assertFalse(r)
        self.assertTrue(self.do_call_time < self.do_2_call_time)
        self.assertIsNone(self.do_3_call_time)


class ResponderActionTests(TestCase):
    def test__unicode(self):
        ic = IssueComment(name='a-comment-name', issue=N(Issue, name='an-issue-name'))
        self.assertEqual('IssueComment: an-issue-name - a-comment-name', ic.__unicode__())

    @patch('issue.models.load_function', spec_set=True)
    def test_execute(self, load_function):
        # Setup the scenario
        target_function = 'do'
        issue = G(Issue)
        r = G(ResponderAction, target_function=target_function, function_kwargs={'foo': 'bar'})
        now = datetime(2014, 8, 11, 15, 0, 0)

        self.assertEqual(0, IssueComment.objects.count())
        load_function.return_value.return_value = True

        # Run the code
        with freeze_time(now):
            r.execute(issue)

        # Verify expectations
        expected_issue_comment_details = {
            'ResponderAction': {
                'success': True,
                'execution_time': int(now.strftime('%s')),
                'target_function': target_function,
                'failure_details': None,
            }
        }
        load_function.assert_called_with(target_function)
        load_function.return_value.assert_called_with(issue, foo='bar')
        self.assertEqual(expected_issue_comment_details, IssueComment.objects.get(
            issue=issue).details)

    @patch('issue.models.load_function', spec_set=True)
    def test_execute_with_failure(self, load_function):
        # Setup the scenario
        target_function = 'fail'
        issue = G(Issue)
        r = G(ResponderAction, target_function=target_function, function_kwargs={'foo': 'bar'})
        now = datetime(2014, 8, 11, 15, 0, 0)

        self.assertEqual(0, IssueComment.objects.count())
        load_function.return_value.side_effect = Exception('what-an-exceptional-message')

        # Run the code
        with freeze_time(now):
            r.execute(issue)

        # Verify expectations
        expected_issue_comment_details = {
            'ResponderAction': {
                'success': False,
                'execution_time': int(now.strftime('%s')),
                'target_function': target_function,
                'failure_details': str(Exception('what-an-exceptional-message'))
            }
        }
        load_function.assert_called_with(target_function)
        load_function.return_value.assert_called_with(issue, foo='bar')
        self.assertEqual(
            expected_issue_comment_details, IssueComment.objects.get(issue=issue).details)


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
        close_open_issue.assert_called_with(issue_name, issue_details)

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
        Assertion()._close_open_issue(issue.name, {})
        self.assertEqual(IssueStatus.Resolved.value, Issue.objects.get(pk=issue.pk).status)
