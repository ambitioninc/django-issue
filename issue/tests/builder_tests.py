from django.test import TestCase
from issue.builder import build_responder
from issue.models import Responder, ResponderAction


class BuildResponderTests(TestCase):
    def test_builder(self):
        watch_pattern = 'That \'impossible\' edge case finally happened...'

        build_responder({
            'watch_pattern': 'That \'impossible\' edge case finally happened...',
            'actions': [
                {
                    'target_function': 'issue.actions.email',
                    'function_kwargs': {
                        'subject': 'Doh!',
                        'recipients': 'john.smith@example.com',
                    },
                    'delay_sec': 30,
                },
                {
                    'target_function': 'issue.actions.email',
                    'function_kwargs': {
                        'subject': 'Doh-2!',
                        'recipients': 'john.smith-boss@example.com',
                    },
                    'delay_sec': 1800,
                },
            ],
        })

        self.assertTrue(Responder.objects.filter(watch_pattern=watch_pattern).exists())
        self.assertTrue(ResponderAction.objects.filter(
            responder__watch_pattern=watch_pattern,
            target_function='issue.actions.email',
            delay_sec=30).exists())
        self.assertEqual({
            'subject': 'Doh!',
            'recipients': 'john.smith@example.com',
        },
            ResponderAction.objects.get(delay_sec=30).function_kwargs)
        self.assertTrue(ResponderAction.objects.filter(
            responder__watch_pattern=watch_pattern,
            target_function='issue.actions.email',
            delay_sec=1800).exists())
        self.assertEqual({
            'subject': 'Doh-2!',
            'recipients': 'john.smith-boss@example.com',
        },
            ResponderAction.objects.get(delay_sec=1800).function_kwargs)
