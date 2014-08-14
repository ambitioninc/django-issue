django-issue Documentation
=============================

========
Overview
========

Sometimes things go wrong in production; if it is a repeating or ongoing error, it makes sense
to represent and track this in some way. This is the purpose of the :class:`Issue` class.
When an error is detected, an :class:`Issue` can be created to store details about it.

Possible advantages of this:

* When something goes wrong, corrective actions that are taken often should not be repeated.
* It gives admins an ability to view at a glance a history of actions taken by the system to address the issue.

Once an :class:`Issue` is created, it is often desirable to *act* on it.  For this, django-issue provides
a :class:`Responder` model.  A :class:`Responder` specifies a pattern to match against :class:`Issue`s; when a pattern matches
for an :class:`Issue` to a 'Responder', the :class:`Responder` executes some configured action.

How are :class:`Issues` created?  They can be easily created by any bit of code.
Alternatively, you can use the :class:`Assertion`. The goal of an :class:`Assertion` 
is to provide a means for detecting when certain properties of your system no longer hold true.

Think of it as a cross between the classic :keyword:`assert` statement available in many programming langauge and traditional software monitoring systems like Nagios.


========
Examples
========

Suppose an error occurs in the middle of night that needs to be addressed in the morning (but is not pressing enough to wake someone up).  We could do something like this::

    from isssue.models import Issue

    try:
        // a problem occurs
    except ValueError as ve:
        Issue.objects.create(name='That *impossible* edge case finally happened...', details=str(ve))


Now when this exception occurs, we will have a record in the database along with details about what happened and when.  Now suppose we want an email notification when this happens.  Well we could add the following::

    from issue.models import Responder, ResponderAction

    r = Responder.objects.create(watch_pattern='That \*impossible\* edge case finally happened')

    ResponderAction.objects.create(responder=r, delay_sec=30, target_function='issue.actions.email',
        function_kwargs={
            'subject': 'Doh!',
            'recipients': 'john.smith@example.com',
        })

There is a helper function for constructing a :class:`Responder` and one or more associated :class:`ResponderAction` from json::

    from issue.builder import build_responder

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
        ]})

The :attr:`delay_sec` may be ommitted; when this happens the ResponderAction will be executed as soon as the Responder matches against an Issue.
