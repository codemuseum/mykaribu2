#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db
import datetime
import random
import Cookie
import urllib
import facebook

# *** Helpers
import helpers as h

# *** Models
from models.pageview import PageView
from models.query import Query
from models.resultview import ResultView

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
        
        if current_user != None:
              page_view.user = current_user

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


# Query Logging
class QueryLoggingsHandler(webapp.RequestHandler):
    def post(self):
        cookies = h.get_default_cookies(self)
        current_user = h.get_current_user(cookies)
        query = Query(query_string = self.request.get('q'))
        
      	query.referrer = self.request.get('referrer')
      	query.url = self.request.get('u')
        if current_user != None:
            query.user = current_user
            if current_user.fb_user_id != None:
                query.fb_user_id = current_user.fb_user_id
                
        query.put()
        self.response.out.write('{status: \'ok\'}')



# ResultView Logging
class ResultViewLoggingsHandler(webapp.RequestHandler):
    def post(self):
        cookies = h.get_default_cookies(self)
        current_user = h.get_current_user(cookies)
        result_view = ResultView()

      	result_view.source = self.request.get('src')
      	result_view.referrer = self.request.get('referrer')
      	result_view.url = self.request.get('u')
        
        if current_user != None:
            result_view.user = current_user
            if current_user.fb_user_id != None:
                result_view.fb_user_id = current_user.fb_user_id
                
            query = Query.gql(
                "WHERE user = :1 AND query_string = :2 ORDER BY created_at DESC", 
                current_user.key(), 
                self.request.get('q')).get()
            if query != None:
                result_view.query = query

        result_view.put()
        self.response.out.write('{status: \'ok\'}')
        
        # Post to facebook wall for the query if the query hasn't already posted to wall
        if current_user != None and query != None and query.fb_wall_post_id == None:
            verbs = ['found', 'looked at', 'searched for']
            verb = verbs[random.randint(0, len(verbs)-1)]
            q_base = "http://apps.facebook.com/mykaribu"
            params_str = urllib.urlencode((('q', query.query_string), ('v', verb), ('suid', current_user.fb_user_id), ('sqid', str(query.key()))))
            q_url = "%s/?%s" % (q_base, params_str)
            message = ":"
            attach = {
                'name': "%s just %s \"%s\"." % (current_user.first_name, verb, query.query_string),
                'link': q_url,
                'caption': '{*actor*} is waiting for your comment',
                'description': 'on this social search.',
                'picture': self.request.get('image_url'),
                'properties': {'They Found:': { 'text': 'this', 'href': "%s/t?u=%s" % (q_base, result_view.url) }}}

            # TODO: Not sure if this access token is the most recent.
            graph = facebook.GraphAPI(current_user.fb_oauth_access_token)
            result = graph.put_wall_post(message=message, attachment=attach)
            
            query.fb_wall_post_id = result['id']
            query.put()
