from google.appengine.ext import webapp, blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import urlfetch
from django.utils import simplejson
from google.appengine.ext import db

from models.question import Question

import helpers as h
import urllib
import logging


class QuestioneerHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        c['data'] = xrange(6)
        r = list()
        r += [[0,0]]
        r += [[253,0]]
        r += [[506,0]]
        r += [[0,253]]
        r += [[253,253]]
        r += [[506,253]]
        c['rects'] = r
        h.render_out(self, 'questioneer.tplt', c)

        
