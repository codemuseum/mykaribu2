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
        h.output(self, '<html><body>Hello world, you are being watched via javascript!<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js" type="text/javascript"></script><script src="/public/js/pageviews.js" type="text/javascript"></script></body></html>')

# Pageviews Logging Handler
class PageViewsHandler(webapp.RequestHandler):
      def post(self):
        cookies = h.get_default_cookies(self)
        if '_pvk' not in cookies or (cookies['_pvk'] == None or cookies['_pvk'] == ''):
            new_session_key = str(datetime.datetime.utcnow()).replace(' ', '') + '-' + str(random.getrandbits(50))
            cookies['_pvk'] = new_session_key

        previous_page_view_for_session = db.GqlQuery("SELECT * FROM PageView WHERE session_id = :1 ORDER BY created_at DESC", cookies['_pvk']).get()

        page_view = PageView()
        current_user = h.get_current_user(cookies)
        
        if current_user != None: # change this to somehow get the user id
              page_view.user_key = str(current_user.key())

        page_view.url = self.request.get('u')
        page_view.normalized_url = self.request.get('u')[:500] # TODO actually normalize URLs according to some logic (e.g. stripping out fb params)
        page_view.referrer = self.request.get('referrer')
        page_view.session_id = cookies['_pvk']
        page_view.ip_address = self.request.remote_addr
        
        if previous_page_view_for_session:
            page_view.session_order = previous_page_view_for_session.session_order + 1
        else:
            page_view.session_order = 0
        
        page_view.put()

        self.response.out.write('{status: \'ok\'}')
