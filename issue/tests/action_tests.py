from django.test import TestCase
from django.core import mail
from django_dynamic_fixture import G

from issue.actions import email
from issue.models import Issue


class EmailTest(TestCase):
    def test_email(self):
        # Setup the scenario
        issue = G(Issue)
        subject = 'A Subject'
        recipients = ['josh.marlow@ambition.com']
        message_txt = 'hello world'

        # Run the code
        email(issue, subject, recipients, message_txt=message_txt)

        # Verify expectations
        self.assertEqual(subject, mail.outbox[0].subject)
        self.assertEqual(recipients, mail.outbox[0].recipients())
        self.assertEqual(message_txt, mail.outbox[0].body)
