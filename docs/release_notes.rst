Release Notes
=============

v3.5.2
------
* Read the Docs config file v2

v3.5.1
------
* Fix manifest

v3.5.0
------
* Python 3.8, 3.9
* Django 3.2, 4.0, 4.1, 4.2
* Drop django 2.2
* Drop python 3.6

v3.2.0
------
* Python 3.7
* Django 2.1
* Django 2.2
* Remove older python and django support

v3.1.2
------
* Fix django warning related to JSONField default value

v3.1.1
------
* Remove 1.10 from setup file

v3.1.0
------
* json field encoder (drop support for django 1.10)

v3.0.0
------
* Add tox to support more versions
* Upgrade to django's JSONField

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
