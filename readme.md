GeoIP Gateway
=============

This WSGI application is meant to function as gateway for a set of HTTP based
services located around the world. It will try to do GeoIP based redirects to
these services or, if there is no preferred server for a location, do a random
selection of a server to be redirected to.

The application will also check regularly if the services are still available
and temporarily mark offline and skip them if necessary.

Redirects happens for subdirectories only. By default `/nexus/...` will be
redirected. The main page will show status information about services and
connections chosen based on your IP address.


Default Set-Up
--------------

By default, the application is configured to serve as gateqay for the [Opencast
](http://opencast.org) Nexus-OSS infrastructure, hence redirecting the `/nexus`
subdirectory and containing Opencast UI templates.


License
-------

This software is licensed under the terms of the GNU General Public License
Version 3 or (at your choice) any later version. The full license can be found
in the file `gpl.txt`.
