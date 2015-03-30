from itertools import chain

from issue.models import Assertion, Issue, ModelAssertion, ModelIssue, Responder


def check_assertions():
    """
    Check all Assertions to see if they are failing.
    """
    failed_assertion_count = 0

    for assertion in chain(Assertion.objects.all(), ModelAssertion.objects.all()):
        if not assertion.check_assertion():
            failed_assertion_count += 1
    return failed_assertion_count


def respond_to_issues():
    """
    Iterate over all open issues and check all Responders against them.
    """
    responders = Responder.objects.all()

    for issue in chain(Issue.objects.get_open_issues(), ModelIssue.objects.get_open_issues()):
        for responder in responders:
            responder.respond(issue)
