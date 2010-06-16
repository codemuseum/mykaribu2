#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

# *** Controller imports
from controllers.admin import AdminHandler
from controllers.admin import AdminHandler
from controllers.admin import AdminPageViewsHandler
from controllers.admin import AdminPathsHandler
from controllers.admin import AdminPathDataHandler
from controllers.admin import AdminUrlAnalyzerHandler
from controllers.admin import AdminUrlSuggestHandler
from controllers.admin import AdminUrlStatsHandler
from controllers.admin import AdminUrlFunnelHandler
from controllers.logging import LoggingHandler, PageViewsHandler
from controllers.framed_result import FramedResultHandler, ShareCountsHandler
from controllers.results import ResultsHandler

# *** Model imports
from models.user import User

# *** Helpers
import helpers as h
import facebook
import datetime

# *** Handlers

# Auth stage 1 - Eventually change this to only redirect when lacking auth
class MainHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        c['current_user'] = h.login_optional(self)
        h.render_out(self, 'main.html', c)

# Auth stage 2 - Eventually change this to catch possibly new tokens on any url
class Auth2Handler(webapp.RequestHandler):
    def get(self):
        cookies = h.get_default_cookies(self)
        c = h.context()
        c['access_token'] = self.request.get("access_token");
        
        user = User.gql("WHERE fb_oauth_access_token = :1", self.request.get("access_token")).get()
        if user != None:
            # If the user currently exists in the DB
            h.set_current_user(cookies, user)
            c['current_user'] = user
        else: 
            # Create the user by looking them up in the graph
            try:
                graph = facebook.GraphAPI(self.request.get("access_token"))
                me = graph.get_object('me')
            except Exception, e:
                me = None
                c['error'] = e

            if me != None:
                new_user = User(
                    fb_user_id = str(me['id']),
                    fb_oauth_access_token = self.request.get("access_token"),
                    fb_oauth_access_token_stored_at = datetime.datetime.utcnow(),
                    first_name = me['first_name'], 
                    last_name = me['last_name'])
                if 'email' in me:
                    new_user.email = me['email']
                new_user.put()
                h.set_current_user(cookies, new_user)
                c['current_user'] = new_user
        
        if 'post_auth_url' in cookies:
            self.redirect(cookies['post_auth_url'])
        else:
            self.redirect('/')

# *** Globals - Need to fix this to find handlers by string
routing =[
    ('/', MainHandler),
    ('/auth2',Auth2Handler),
    ('/admin',AdminHandler),
    ('/admin/pageviews',AdminPageViewsHandler),
    ('/admin/paths',AdminPathsHandler),
    ('/admin/paths/data.json',AdminPathDataHandler),
    ('/admin/url-analyzer',AdminUrlAnalyzerHandler),
    ('/admin/url-suggest',AdminUrlSuggestHandler),
    ('/admin/urls/stats.json', AdminUrlStatsHandler),
    ('/admin/urls/funnel.json', AdminUrlFunnelHandler),
    ('/logging',LoggingHandler),
    ('/t',FramedResultHandler),
    ('/share_counts',ShareCountsHandler),
    ('/results',ResultsHandler),
    ('/pageviews.json',PageViewsHandler)
    ]

# *** Init code
def main():
    h.init()
    global cfg
    cfg = h.cfg
    
    # configure and start the actual app
    global routing
    application = webapp.WSGIApplication(routing,
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
