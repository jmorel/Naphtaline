#!/usr/local/bin/python2.5
import cherrypy

from naphtaline import Naphtaline
from urls import setRoutes

# creating the app instance
root = Naphtaline()

# attach configuration to the application
cherrypy.config.update('etc/site.cfg')

# mount the application on the '/' base path with the desired configuration
app = cherrypy.tree.mount(root=None, config='etc/app.cfg')

# setting up authorized routes
# we control exactly what url are authorized, thus preventing people from passing values into arguments only supposed to receive POST values.
dispatch = setRoutes(root)
app.merge({'/': {'request.dispatch': dispatch}})

# start the CherryPy engine
cherrypy.engine.start()
cherrypy.engine.block()
