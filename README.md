Access to tolino cloud with Python 3
====================================

**TolinoCloud** is an inofficial implementation of the tolino cloud
web reader REST API.

The *tolino ebook reader* is sold by several different partners, most
of them based in Germany, e.g. Thalia or Hugendubel.

The tolino reader comes with its own cloud storage service.

Run by Telekom / T-Systems, the tolino cloud is used to both

- store / backup ebooks purchased by the user

and

- allow the user to upload / sync own files to the user's device(s)

Users can manage their purchased ebooks and uploads through a web
interface, the tolino web reader, which is a HTML5/javascript
application within the user's browser.

Command line client to tolino cloud
===================================

**tolinoclient.py** executes the web reader's REST API commands
to allow scripted access to a few very basic commands:

- list ebooks / uploads
- upload a file to the user's personal tolino cloud storage
- download a file from the tolino cloud
- delete an ebook / upload
- list devices connected to an account
- unregister a device from an account

Status
======

**It may be buggy. Bad things might happen. You were warned.**

Works with Hugendubel.de (partner 13) and Thalia.de (partner 3) only.
(More may be added in the future.)

Tested with Linux, only. Patches welcome. Handle with care.

To-Do
=====

Better error handling.

More REST API calls (e.g. meta data edit, cover image upload).

Support for more resellers.

Hey, tolino developers at Telekom / T-Systems, please look at
the comments in tolinocloud.py. It'd be really nice to get the
specifications for the REST API. Thanks!

License
=======

**TolinoCloud** is distributed under the terms of the
[GNU Lesser General Public License 2.1](http://www.gnu.org/licenses/lgpl-2.1.txt).
