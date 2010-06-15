#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db
import datetime
import random
import Cookie

# *** Helpers
import helpers as h

# *** Models
from models.pageview import PageView

# *** Handlers

# Logging main handler
class LoggingHandler(webapp.RequestHandler):
	def get(self):
		h.output(self, '<html><body>Hello world, you are being watched via javascript!<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js" type="text/javascript"></script><script src="/public/javascripts/pageviews.js" type="text/javascript"></script></body></html>')

# Pageviews Logging Handler
class PageViewsHandler(webapp.RequestHandler):
  	def post(self):
		if '_pvk' not in self.request.cookies or (self.request.cookies['_pvk'] == None or self.request.cookies['_pvk'] == ''):
			new_session_key = str(datetime.datetime.utcnow()).replace(' ', '') + '-' + str(random.getrandbits(50))
	  		# self.response.set_cookie('_pvk', new_session_key, max_age=360000000)
			self.response.headers.add_header('Set-Cookie', '_pvk='+new_session_key+'; path=/; expires=Wednesday, 01-Jan-2030 00:00:00 GMT') 
			self.request.cookies['_pvk'] = new_session_key # need to do this so the logging below can write it

		previous_page_view_for_session = db.GqlQuery("SELECT * FROM PageView WHERE session_id = :1 ORDER BY created_at DESC", self.request.cookies['_pvk']).get()

		page_view = PageView()

		if False: # change this to somehow get the user id
	  		page_view.user_id = get_current_user().id

		page_view.url = self.request.get('u')
		page_view.normalized_url = self.request.get('u')[:500] # TODO actually normalize URLs according to some logic (e.g. stripping out fb params)
		page_view.referrer = self.request.get('referrer')
		page_view.session_id = self.request.cookies['_pvk']
		page_view.ip_address = self.request.remote_addr
		
		if previous_page_view_for_session:
			page_view.session_order = previous_page_view_for_session.session_order + 1
		else:
			page_view.session_order = 0
		
		page_view.put()

		self.response.out.write('{status: \'ok\'}')
