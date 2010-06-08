#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

# *** Helpers
import helpers as h

# *** Handlers

# Admin main handler
class AdminHandler(webapp.RequestHandler):
    def get(self):
        h.output(self, "admin page")
