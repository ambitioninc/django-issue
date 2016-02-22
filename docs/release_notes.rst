Release Notes
=============

v1.2.0
------
* Django 1.9 support

v1.1.0
------
* Django 1.8 support and removal of 1.6 support

v1.0.5
------
* Additional tweak to the behavior of maybe_open_issue

v1.0.4
------
* Remove south as a dependency

v1.0.3
------
* Tweak to the behavior of reopen_issue

v1.0.2
------
* Tweak to the behavior of maybe_open_issue

v1.0.1
------
* Added a helper method, maybe_open_issue, to the IssueManager class
* This implements logic that's begun to repeat in my Issue use cases

v1.0.0
------
* Added Django 1.7 compatability
* ``ModelAssertion`` and ``BaseAssertion``'s ``.check()`` methods were renamed
to ``check_assertion()``

v0.1
----

* This is the initial release of django-issue.
