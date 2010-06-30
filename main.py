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
from google.appengine.api import urlfetch

# *** Controller imports
from controllers.admin import AdminHandler, AdminPageViewsHandler, AdminPageViewsDataHandler, AdminPathsHandler, AdminPathDataHandler, AdminUrlAnalyzerHandler, AdminUrlSuggestHandler, AdminUrlStatsHandler, AdminUrlFunnelHandler, AdminQueriesHandler, AdminQueriesDataHandler, AdminResultViewsHandler, AdminResultViewsDataHandler, AdminUsersHandler, AdminUsersDataHandler, AdminUserGraphsHandler, AdminUserGraphsDataHandler, AdminPageViewNormalizerHandler, AdminInstallMetricsHandler, AdminInstallMetricsDataHandler, AdminInstallMetricsSummaryHandler, AdminInstallMetricCalculatorHandler, AdminOrganicSearchMetricsHandler, AdminOrganicSearchMetricsDataHandler, AdminOrganicSearchMetricsSummaryHandler, AdminOrganicSearchMetricCalculatorHandler, AdminPostInstallActivityMetricsHandler, AdminPostInstallActivityMetricsDataHandler, AdminPostInstallActivityMetricsSummaryHandler, AdminPostInstallActivityMetricCalculatorHandler, AdminKValueMetricsHandler, AdminKValueMetricsDataHandler, AdminKValueMetricsSummaryHandler, AdminKValueMetricCalculatorHandler, AdminKValueMetricCalculatorClearerHandler
from controllers.mk_logging import LoggingHandler, PageViewsHandler, QueryLoggingsHandler, ResultViewLoggingsHandler, PostLoginSewingLoggingsHandler
from controllers.framed_result import FramedResultHandler, ShareCountsHandler
from controllers.results import ResultsHandler, QuestionUploader, ServeHandler, QuestionAdmin
from controllers.stash import StashHandler
from controllers.questioneer import QuestioneerHandler
from controllers.users import FetchUserGraphHandler

# *** Model imports
from models.user import User

# *** Helpers
import helpers as h
import facebook
import datetime
import logging

# *** Handlers

class CookieTestHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        h.render_out(self, 'cookie_test.tplt', c)
        
# Auth stage 1 - Eventually change this to only redirect when lacking auth
class MainHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        c['current_user'] = h.login_optional(self)
        h.render_out(self, 'main.html', c)

# Auth stage 2 - Eventually change this to catch possibly new tokens on any url
class Auth2Handler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        logging.info("***Auth2")
        cookies = h.get_default_cookies(self)
        c['cookies'] = cookies
        logging.info("***cookies: "+str(cookies))
        c['access_token'] = self.request.get("access_token")
        
        if self.request.get("access_token") == '':
            logging.error("No access token set, but we expected on %s" % str(self.request.url))
        else:
            logging.warning("Got access token %s" % self.request.get("access_token"))
        
        user = User.gql("WHERE fb_oauth_access_token = :1", self.request.get("access_token")).get()
        if user != None:
            # If the user currently exists in the DB
            logging.info("***SCU1")
            h.set_current_user(cookies, user)
            logging.info("***cookies: "+str(cookies))
            c['current_user'] = user
        else: 
            # Look user up in graph, and either find them in the DB or create them if they don't exist
            try:
                graph = facebook.GraphAPI(self.request.get("access_token"))
                me = graph.get_object('me')
            except Exception, e:
                logging.error(
                    "ERROR!  Failed to access Facebook Graph for access_token=" + 
                    self.request.get("access_token") +
                    "::" + str(e)) 
                me = None
                c['error'] = e

            if me != None:
                og_user = User.gql("WHERE fb_user_id = :1", str(me['id'])).get()
                
                if og_user == None:
                    new_user = User(
                        fb_user_id = str(me['id']),
                        fb_oauth_access_token = self.request.get("access_token"),
                        fb_oauth_access_token_stored_at = datetime.datetime.utcnow(),
                        first_name = me['first_name'], 
                        last_name = me['last_name'])
                    if 'email' in me:
                        new_user.email = me['email']
                    new_user.put()
                    logging.info("***SCU2")
                    h.set_current_user(cookies, new_user)
                    logging.info("***cookies: "+str(cookies))
                    c['current_user'] = new_user
                    
                else: # Update auth token for user because it's out of date
                    og_user.fb_oauth_access_token = self.request.get("access_token")
                    og_user.fb_oauth_access_token_stored_at = datetime.datetime.utcnow()
                    og_user.put()
                    logging.info("***SCU3")
                    h.set_current_user(cookies, og_user)
                    logging.info("***cookies: "+str(cookies))
                    c['current_user'] = og_user
        
        if 'current_user' in c and 'post_auth_url' in cookies:
            logging.info("***Sent to post_auth_url")
            redirect_to_url = cookies['post_auth_url']
            del cookies['post_auth_url']
            c['top_redirect_url'] = redirect_to_url
            # self.redirect(redirect_to_url)
            
            # Reparse user graph on login
            graph_task_url = 'http://'+self.request.host+'/users/tasks/fetchgraph?key='+str(c['current_user'].key())
            rpc = urlfetch.create_rpc(deadline=1)
            urlfetch.make_fetch_call(rpc,graph_task_url)
            try:
              result_body = rpc.get_result()
            except urlfetch.DownloadError, e:
              logging.error("User Auth couldn't contact graph task url %s, got error:%s" % (graph_task_url, str(e)))
            
        else:
            logging.info("***Sent home due to lack of post_auth or current_user")
            c['top_redirect_url'] = h.cfg['fb_url']
            # self.redirect('/')
        
        h.render_out(self, "redirector.tplt", c)


# *** Globals - Need to fix this to find handlers by string
routing =[
    ('/',ResultsHandler),
    ('/test',MainHandler),
    ('/auth2',Auth2Handler),
    ('/admin',AdminHandler),
    ('/admin/pageviews',AdminPageViewsHandler),
    ('/admin/pageviews/data.json',AdminPageViewsDataHandler),
    ('/admin/pageviews/normalizer', AdminPageViewNormalizerHandler),
    ('/admin/users',AdminUsersHandler),
    ('/admin/users/data.json',AdminUsersDataHandler),
    ('/admin/usergraphs',AdminUserGraphsHandler),
    ('/admin/usergraphs/data.json',AdminUserGraphsDataHandler),
    ('/admin/querys',AdminQueriesHandler),
    ('/admin/querys/data.json',AdminQueriesDataHandler),
    ('/admin/resultviews',AdminResultViewsHandler),
    ('/admin/resultviews/data.json',AdminResultViewsDataHandler),
    ('/admin/paths',AdminPathsHandler),
    ('/admin/paths/data.json',AdminPathDataHandler),
    ('/admin/url-analyzer',AdminUrlAnalyzerHandler),
    ('/admin/url-suggest',AdminUrlSuggestHandler),
    ('/admin/urls/stats.json', AdminUrlStatsHandler),
    ('/admin/urls/funnel.json', AdminUrlFunnelHandler),
    ('/admin/installmetrics',AdminInstallMetricsHandler),
    ('/admin/installmetrics/data.json',AdminInstallMetricsDataHandler),
    ('/admin/installmetrics/summary',AdminInstallMetricsSummaryHandler),
    ('/admin/installmetrics/calculator.json',AdminInstallMetricCalculatorHandler),
    ('/admin/organicsearchmetrics',AdminOrganicSearchMetricsHandler),
    ('/admin/organicsearchmetrics/data.json',AdminOrganicSearchMetricsDataHandler),
    ('/admin/organicsearchmetrics/summary',AdminOrganicSearchMetricsSummaryHandler),
    ('/admin/organicsearchmetrics/calculator.json',AdminOrganicSearchMetricCalculatorHandler),
    ('/admin/postinstallactivitymetrics',AdminPostInstallActivityMetricsHandler),
    ('/admin/postinstallactivitymetrics/data.json',AdminPostInstallActivityMetricsDataHandler),
    ('/admin/postinstallactivitymetrics/summary',AdminPostInstallActivityMetricsSummaryHandler),
    ('/admin/postinstallactivitymetrics/calculator.json',AdminPostInstallActivityMetricCalculatorHandler),
    ('/admin/kvaluemetrics',AdminKValueMetricsHandler),
    ('/admin/kvaluemetrics/data.json',AdminKValueMetricsDataHandler),
    ('/admin/kvaluemetrics/summary',AdminKValueMetricsSummaryHandler),
    ('/admin/kvaluemetrics/calculator.json',AdminKValueMetricCalculatorHandler),
    ('/admin/kvaluemetrics/clearer.json',AdminKValueMetricCalculatorClearerHandler),
    ('/logging',LoggingHandler),
    ('/t',FramedResultHandler),
    ('/share_counts',ShareCountsHandler),
    ('/results',ResultsHandler),
    ('/pageviews.json',PageViewsHandler),
    ('/storequeries.json',QueryLoggingsHandler),
    ('/storeresultclicks.json',ResultViewLoggingsHandler),
    ('/postlogin.json', PostLoginSewingLoggingsHandler),
    ('/cookie_test', CookieTestHandler),
    ('/stash', StashHandler),
    ('/qup',QuestionUploader),
    ('/serve/([^/]+)?',ServeHandler),
    ('/qad',QuestionAdmin),
    ('/questioneer',QuestioneerHandler),
    ('/users/tasks/fetchgraph',FetchUserGraphHandler)
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
