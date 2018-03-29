Release Notes
=============

v2.1.0
------
* Add tox to support more versions

v2.0.0
------
* Remove python 2.7 support
* Remove python 3.4 support
* Remove Django 1.9 support
* Remove Django 1.10 support
* Add Django 2.0 support

v1.4.0
------
* Python 3.6 support
* Django 1.10 support
* Django 1.11 support
* Remove Django 1.8 support

v1.3.0
------
* Python 3.5 support, remove django 1.7 support

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
