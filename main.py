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
from controllers.logging import LoggingHandler
from controllers.framed_result import FramedResultHandler, ShareCountsHandler
from controllers.results import ResultsHandler

# *** Helpers
import helpers as h

# *** Handlers

# Auth stage 1 - Eventually change this to only redirect when lacking auth
class MainHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        self.redirect('https://graph.facebook.com/oauth/authorize?'
                      +'type=user_agent&display=page&client_id='
                      +cfg['app_id']+'&redirect_uri='
                      +cfg['direct_url']
                      +'/auth2&scope=publish_stream')

# Auth stage 2 - Eventually change this to catch possibly new tokens on any url
class Auth2Handler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        h.render_out(self, 'main.html', c)

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
