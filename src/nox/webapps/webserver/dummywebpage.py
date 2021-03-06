# Copyright 2008 (C) Nicira, Inc.
#
# This file is part of NOX.
#
# NOX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# NOX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NOX.  If not, see <http://www.gnu.org/licenses/>.

"""Example web page served through the webserver component.

This example component demonstrates serving both dynamically and
statically generated content using the webserver component.

Dynamic content is served by subclassing the TwistedWeb Resource class
(defined in twisted.web.resource.Resource), providing implementations
for methods named "render_<HTTP Request Method>" to take any desired
actions and return appropriate content, and registering that class for
a specific URL using the install_resource method of the webserver
component.  The DummyPageResource class defined below illustrates a
trivial implementation of a TwistedWeb Resource subclass serving a
very simple page in response to a GET request.  The dummywebpage class
below, implementing the dummywebpage component, registers a
DummyPageInstance resource its install method.

Static content comes from a static_www subdirectory in a component's
directory.  The subdirectory tree under this directory will be made
available below a URL of the form:

     /static/<buildnr>/<module path>/

where:

    <buildnr> is the build number given to this software version.  If
         a build number is not specifically provided when configure is
         run, it defaults to zero.  Since it changes on a build by
         build basis, the safest method is to dynamically generate
         this part of the path.  The example page generated by the
         DummyPageResource class below demonstrates this.

    <module_path> is the path to the module.  This module path for
         this component is "nox/webapps/webserver".  Other components
         will have different module paths, depending on where they
         reside in the NOX source tree.

Dynamic page resources should NOT be installed on paths within the
static tree.

If creating your own module using this one as a template, be sure to
look at the following related files in this component directory as
well:

     meta.xml: This file records the component dependencies.  Refer to
         the section for the dummywebpage component to setup your own
         component.

     Makefile.am: If the new component is in a new subdirectory, a
         Makefile.am will be required for it.  Refer to the one in
         this component's directory.  Particularly important for
         proper operation of web content is correct defintion of the
         MODULE, MODULE_BASE_PATH, and MODULE_BASE_ESCAPE variables.
         The dependencies on the all-local, clean-local, and
         install-exec-hook targets are required, but the commands
         under the dependency declaration line should NOT be copied
         into the new Makefile.am.

If the proper dependencies are specified in meta.xml, NOX can be
started with the webserver serving that content by simply ensuring the
component name is included on the nox command line.  In this example,
to start NOX so that it just server the dummy page, start nox as:

      nox_core dummywebpage

By default, the webserver will attempt to run on port 80 and 443,
which will fail if run as a regular user.  To get an unencrypted
server to run on a non-standard port, use a command like:

      nox_core webserver=port=8888 dummywebpage

"""

from nox.coreapps.pyrt.pycomponent import *
from nox.lib.core import *

from nox.webapps.webserver import webserver

from twisted.web.resource import Resource

class DummyPageResource(Resource):
    def __init__(self, component):
        # Using component reference to get at webserver component to
        # determine the base path for static content.
        self.component = component

    # If generating a lot of dynamic content, a templating system is a
    # very helpful.  We know of successful use of this framework with
    # the Mako templating system, but any system available and
    # familiar should work fine.
    def render_GET(self, request):
        return """\
<html>
  <head><title>NOX Dummy Web Page</title></head>
  <body>
     <h1>NOX Dummy Web Page</h1>
     <p>Congratulations, the NOX web server is working.</p>
     <img src="%s/nox/webapps/webserver/happy_face.png" alt="Happy face image from static content.">
  </body>
</html>
""" % (self.component.webserver.siteConfig["staticBase"],)

class dummywebpage(Component):

    def __init__(self, ctxt):
        Component.__init__(self, ctxt)
        self.webserver = None

    def install(self):
        # Get a reference to the webserver component
        self.webserver = self.resolve(str(webserver.webserver))
        # tell webserver that all authentication initialization is
        # done.  This is a wart to allow pluggable authentication
        self.webserver.authui_initialized = True

        # Install a dynamically generated page
        self.webserver.install_resource("/dummy.html", DummyPageResource(self))
        # Set the default web server URL served when "/" is requested.
        # This should only be called by one component or the final
        # result will be dependent on component load order, which can
        # vary.
        self.webserver.default_uri = "/dummy.html"

    def getInterface(self):
        return str(dummywebpage)

def getFactory():
    class Factory:
        def instance(self, ctxt):
            return dummywebpage(ctxt)

    return Factory()
