django-issue Documentation
=============================

==========
Overview
==========

Sometimes things go wrong in production; if it is a repeating or ongoing error, it makes sense
to represent and track this in some way. This is the purpose of the :class:`Issue` class.
When an error is detected, an :class:`Issue` can be created to store details about it.

Possible advantages of this:
1) When something goes wrong, corrective actions that are taken often should not be repeated.
2) It gives admins an ability to view at a glance a history of

Once an :class:`Issue` is created, it is often desirable to *act* on it.  For this, django-issue provides
a 'Responder' mode.  A 'Responder' specifies a pattern to match against :class:`Issue`s; when a pattern matches
for an :class:`Issue` to a 'Responder', the Responder executes some configured action.

How are :class:`Issues` created?  They can be easily created by any bit of code.
Alternatively, you can specify :class:`Assertion`s. The goal of an :class:`Assertion` is to provide a cross between the classic :keyword:`assert` statement available in many programming langauge and traditional software monitoring systems like Nagios.

An :class:`Assertion` provides a means for detecting when certain properties of your system no longer hold true.

