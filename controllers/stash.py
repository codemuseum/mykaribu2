from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from django.utils import simplejson
import helpers as h
import urllib
import logging
        
class StashHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        h.render_out(self, 'stash.tplt', c)
        
