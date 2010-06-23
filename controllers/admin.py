#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from django.utils import simplejson
import datetime
from urlparse import urlparse
import cgi
import logging

# *** Helpers
import helpers as h

# *** Models
from models.pageview import PageView
from models.query import Query
from models.resultview import ResultView
from models.user import User
from models.installmetric import InstallMetric

# *** Handlers

class AdminHelper:
    @staticmethod
    def writePaginatedDataJson(handler, model, cursor_param=None, order_by = '-created_at'):
        query = model.all()
        query.order(order_by)
        if cursor_param != None:
            query.with_cursor(cursor_param)
        results = query.fetch(1000)

        handler.response.out.write(simplejson.dumps({'status': 'ok', 'results': AdminHelper.MapToHash(results), 'cursor': str(query.cursor()), 'count': len(results) }))

    @staticmethod
    def ToHash(entity):
        result = {'__key__': str(entity.key())}
        for prop in entity.__class__.properties():
            val = getattr(entity, prop)
            if isinstance(val, db.Model):
                result[prop] = '<a href="/admin/'+val.__class__.__name__.lower()+'s#key_'+str(val.key())+'" target="_blank">'+str(val.key())+'</a>'
            elif isinstance(val, basestring):
                result[prop] = str(val.encode('utf-8'))
            else:
                result[prop] = str(val)
        return result

    @staticmethod
    def MapToHash(entity_array):
        return map(lambda entity: AdminHelper.ToHash(entity), entity_array)
      

# Admin main handler
class AdminHandler(webapp.RequestHandler):
    def get(self):
        h.output(self, "Admin: <a href='/admin/pageviews'>Page Views</a> | <a href='/admin/users'>Users</a>  | <a href='/admin/querys'>Searches</a> | <a href='/admin/resultviews'>Result Views</a> | <a href='/admin/installmetrics'>User Install Metrics</a> | <a href='/admin/installmetrics/summary'>Summary Install Metrics</a> | <a href='/admin/paths'>Navigation Paths</a> | <a href='/admin/url-analyzer'>URL Analyzer</a> |  <a href='/admin/pageviews/normalizer'>Page View URL Normalizer</a>")

class AdminPageViewsHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        c['model'] = 'pageview'
        c['model_properties'] = sorted(PageView.properties())
        h.render_out(self, 'admin.tplt', c)

class AdminPageViewsDataHandler(webapp.RequestHandler):
    def post(self):
        AdminHelper.writePaginatedDataJson(self, PageView, self.request.get('cursor'))

class AdminUsersHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        c['model'] = 'user'
        c['model_properties'] = sorted(User.properties())
        h.render_out(self, 'admin.tplt', c)

class AdminUsersDataHandler(webapp.RequestHandler):
    def post(self):
        AdminHelper.writePaginatedDataJson(self, User, self.request.get('cursor'))


class AdminQueriesHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        c['model'] = 'query'
        c['model_properties'] = sorted(Query.properties())
        h.render_out(self, 'admin.tplt', c)

class AdminQueriesDataHandler(webapp.RequestHandler):
    def post(self):
        AdminHelper.writePaginatedDataJson(self, Query, self.request.get('cursor'))


class AdminResultViewsHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        c['model'] = 'resultview'
        c['model_properties'] = sorted(ResultView.properties())
        h.render_out(self, 'admin.tplt', c)

class AdminResultViewsDataHandler(webapp.RequestHandler):
    def post(self):
        AdminHelper.writePaginatedDataJson(self, ResultView, self.request.get('cursor'))

class AdminPathsHandler(webapp.RequestHandler):
    def get(self):
        h.output(self, '<html><head><style>.end{background-color:#f1f1f1; color:#555; font-size:8px; font-weight:bold;}.path {padding:10px;border-bottom:1px dashed #ccc;margin-top:5px;} .path:hover {background-color:#ddd;}.path a {cursor:pointer;color:#383838;text-decoration:none}.path a:hover{text-decoration:underline}.clear{float:none;clear:both;height:1px}.percent{float:left;width:4%;padding-left:1%;}.numeric{float:left;width:4%;padding-left:1%;}.url{float:left;width:89%;padding-left:1%}.sub-paths{margin-left:2%; border-left:1px solid #ccc;padding-left:10px;} .path.collapsed .sub-paths {display:none}</style></head><body>Paths:<div id="paths"></div><script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js" type="text/javascript"></script><script src="/public/js/admin/paths.js" type="text/javascript"></script></body></html>')
        

class AdminPathDataHandler(webapp.RequestHandler):
    def post(self):
        session_ids = None
        query = PageView.all()
        query.order('-created_at')
        query.filter('session_order =', int(self.request.get('session_order')))
        if self.request.get('session_ids') != '':
            query.filter('session_id IN', simplejson.loads(self.request.get('session_ids')))
        
        cursor = self.request.get('cursor')
        if cursor != None:
            query.with_cursor(cursor)

        page_views = query.fetch(1000)
        page_views.sort(lambda a,b: cmp(a.normalized_url, b.normalized_url))
        collapsed_page_views = []
        current_url = None
        current_count = 0
        current_session_ids = []
        
        for page_view in page_views:
            if current_url == page_view.normalized_url:
                current_count += 1
                current_session_ids.append(page_view.session_id)
            else:
                if current_count > 0:
                    collapsed_page_views.append({'url': current_url, 'count': current_count, 'session_ids': current_session_ids  })
                current_url = page_view.normalized_url
                current_count = 1
                current_session_ids = [page_view.session_id]
        
        if current_count > 0:
            collapsed_page_views.append({'url': current_url, 'count': current_count, 'session_ids': current_session_ids })
        current_url = None
        current_count = 0
        
        self.response.out.write(simplejson.dumps({'status': 'ok', 'cursor': str(query.cursor()), 'results': collapsed_page_views, 'total_pageviews_in_query': len(page_views) }))


class AdminUrlAnalyzerHandler(webapp.RequestHandler):
    def get(self):
        h.output(self, '<html><head><link rel="stylesheet" href="/public/css/jquery.autocomplete.css" type="text/css" /><style>.loading{font-size:83%; color:#92ABC2;padding:10px}#url-input {width:80%} .stats {font-size:83%; color:#999; padding:8px} .button {padding:3px 7px; background-color:#999; border:1px solid #333; cursor:pointer; color:#fff;}.url {padding-bottom:20px;} #analyzer {position:relative;} #entrances-arrow{top:47%;left:30%; width:64px; height:64px; position:absolute;} #exits-arrow{top:47%;left:61%; width:64px; height:64px; position:absolute;} #entrances, #page, #exits {width:30%; border:1px solid #eee; float:left; height:90%; display:table-cell; vertical-align:middle;margin-left:1%;overflow:auto} #page {text-align:center; line-height:100%; height:50%; padding-top:20%;-moz-box-shadow:5px 5px 5px #ccc;box-shadow: 5px 5px 5px #ccc;-webkit-box-shadow: 5px 5px 5px #ccc; }#entrances {text-align:right}.entrance, .exit {border-bottom:1px dashed #ccc; padding:10px} .entrance:nth-child(odd), .exit:nth-child(odd){background-color:#F5FAFF}</style></head><body><div class="url">URL: <input type="text" name="url" id="url-input" autocomplete="off" /> <a onclick="UrlAnalyzer.loadUrl();" class="button">Lookup</a><br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="checkbox" name="double_count" id="double-count" checked disabled="true" /> <label for="double-count">Allow Double-Counting of this URL in a Single Session</label></div><div id="analyzer"><div id="entrances-arrow"><img src="/public/images/admin/gray-right-arrow.png" width="64"/></div><div id="exits-arrow"><img src="/public/images/admin/gray-right-arrow.png" width="64"/></div><div id="entrances"></div><div id="page"></div><div id="exits"></div><div style="clear:both"></div></div><script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js" type="text/javascript"></script><script src="/public/js/jquery.autocomplete.min.js" type="text/javascript"></script><script src="/public/js/admin/url-analyzer.js" type="text/javascript"></script></body></html>')

class AdminUrlSuggestHandler(webapp.RequestHandler):
    def get(self):
        search_term = self.request.get('q')
        query = PageView.all()
        query.order('-normalized_url')
        query.filter('normalized_url >=',search_term)
        query.filter('normalized_url <', search_term+"\ufffd")
        page_views = query.fetch(1000)
        
        unique_url_hash = {} 
        for page_view in page_views: 
            unique_url_hash[page_view.normalized_url] = 1
        unique_urls = unique_url_hash.keys()
        unique_urls.sort()

        self.response.out.write("\n".join(unique_urls))
        
class AdminUrlStatsHandler(webapp.RequestHandler):
    def post(self):
        url = self.request.get('url')
        query = PageView.all()
        query.order('session_id')
        query.filter('normalized_url =', url)
        cursor = self.request.get('cursor')
        if cursor != None:
            query.with_cursor(cursor)
        page_views = query.fetch(1000)
        
        page_views_by_session_id = {}
        for page_view in page_views: 
            if page_view.session_id in page_views_by_session_id:
                page_views_by_session_id[page_view.session_id] += 1
            else:
                page_views_by_session_id[page_view.session_id] = 1
        
        self.response.out.write(simplejson.dumps({'status': 'ok', 'results': page_views_by_session_id, 'cursor': str(query.cursor()), 'total_pageviews': len(page_views), 'total_sessions': len(page_views_by_session_id.keys()) }))
        
class AdminUrlFunnelHandler(webapp.RequestHandler):
    def post(self):
        mode = self.request.get('mode')
        if mode == 'entrances':
            mode_session_order_add_amount = -1
        else:
            mode_session_order_add_amount =  1
        url = self.request.get('url')
        query = PageView.all()
        query.order('session_id')
        query.filter('normalized_url =', url)
        cursor = self.request.get('cursor')
        if cursor != None:
            query.with_cursor(cursor)
        page_views = query.fetch(1000)
        
        entrances_hash = {}
        for page_view in page_views:
            if mode == 'entrances' and page_view.session_order == 0:
                if '[direct]' in entrances_hash:
                    entrances_hash['[direct]'] += 1
                else:
                    entrances_hash['[direct]'] = 1
            
            else:
                q_s = "SELECT * FROM PageView WHERE session_id = :1 AND session_order = :2"
                entrance_page_view = db.GqlQuery(q_s, page_view.session_id, page_view.session_order + mode_session_order_add_amount).get()
                if entrance_page_view:
                    if entrance_page_view.normalized_url in entrances_hash:
                        entrances_hash[entrance_page_view.normalized_url] += 1
                    else:
                        entrances_hash[entrance_page_view.normalized_url] = 1
                elif mode == 'exits':
                    if '[leave-site]' in entrances_hash:
                        entrances_hash['[leave-site]'] += 1
                    else:
                        entrances_hash['[leave-site]'] = 1
                        
        
        self.response.out.write(simplejson.dumps({'status': 'ok', 'mode': mode, 'cursor': str(query.cursor()), 'results': entrances_hash, 'total_entrances': len(entrances_hash.keys()), 'total_entrance_pageviews': sum(entrances_hash.values()) }))
                        

class AdminPageViewNormalizerHandler(webapp.RequestHandler):
    def get(self):
        h.output(self, '<html><head><style></style></head><body><div>Normalization Status: <span id="status">Not started, complete below.</span></div><div><textarea id="filtered-params" style="height:15em;width:50%">fb_sig,fb_sig_in_iframe,fb_sig_iframe_key,fb_sig_locale,fb_sig_in_new_facebook,fb_sig_time,fb_sig_added,fb_sig_profile_update_time,fb_sig_expires,fb_sig_user,fb_sig_session_key,fb_sig_ss,fb_sig_cookie_sig,fb_sig_ext_perms,fb_sig_country,fb_sig_api_key,fb_sig_app_id,auth,infb</textarea><br/>Fill in the above with a comma-separated list</div><div><a id="normalize-button" href="#">NORMALIZE NOW!</a><script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js" type="text/javascript"></script><script src="/public/js/admin/url-normalizer.js" type="text/javascript"></script></body></html>')
    
    def post(self):
        query = PageView.all()
        query.order('-created_at')
        cursor = self.request.get('cursor')
        if cursor != None:
            query.with_cursor(cursor)

        filter_out_params = {}
        for param in str(self.request.get('filtered_params')).split(','):
            filter_out_params[param.strip()] = True

        page_views = query.fetch(100)

        for page_view in page_views:            
            parsed = urlparse(page_view.url)
            params = cgi.parse_qs(parsed.query)

            new_url = parsed.scheme + "://" + parsed.netloc + parsed.path
            new_param_string = ''

            for key in sorted(params.keys()):
              if key not in filter_out_params or filter_out_params[key] == False:
                for val in params[key]:
                  if new_param_string != '':
                    new_param_string += '&'
                  new_param_string += key + "=" + val

            if len(new_param_string) == 0:
              page_view.normalized_url = new_url
            else:
              page_view.normalized_url = new_url + "?" + new_param_string

            page_view.put()
        
        self.response.out.write(simplejson.dumps({'status': 'ok', 'cursor': str(query.cursor()), 'count': len(page_views) }))


class AdminInstallMetricsHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        c['model'] = 'installmetric'
        c['model_properties'] = sorted(InstallMetric.properties())
        h.render_out(self, 'admin.tplt', c)

class AdminInstallMetricsDataHandler(webapp.RequestHandler):
    def post(self):
        AdminHelper.writePaginatedDataJson(self, InstallMetric, self.request.get('cursor'), order_by = '-updated_at')


class AdminInstallMetricsSummaryHandler(webapp.RequestHandler):
    def get(self):
        last_metric_at = InstallMetric.gql("ORDER BY updated_at DESC").get()
        if last_metric_at == None:
            last_metric_at = "[Never]"
        else:
            last_metric_at = last_metric_at.updated_at
        
        h.output(self, '<html><head><link href="/public/css/admin/admin.css" type="text/css" rel="stylesheet" /></head><body><div id="loading-msg">Loading...</div><div>Install Metric Re-Calculation Status: <span id="status">Last Run at: '+str(last_metric_at)+'</span> <a id="calculate-button" href="#">RE-CALCULATE NOW!</a></div><div>Total Users: <span id="total-users">...</span></div><div>Users From Ads: <span id="total-from-ads">...</span></div><div>Users From Newsfeeds: <span id="total-from-newsfeeds">...</span></div><div>Users From Unknown: <span id="total-from-unknown">...</span></div><script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js" type="text/javascript"></script><script src="/public/js/admin/install-metrics.js" type="text/javascript"></script></body></html>')

    def post(self):
        query = InstallMetric.all()
        query.order('-updated_at')
        cursor = self.request.get('cursor')
        if cursor != None:
            query.with_cursor(cursor)

        install_metrics = query.fetch(1000)
        total_users = 0
        total_from_ads = 0
        total_from_newsfeeds = 0
        total_from_unknown = 0
        for install_metric in install_metrics:
            total_users += 1
            if install_metric.installed_via_ad == True:
                total_from_ads += 1
            elif install_metric.installed_via_newsfeed == True:
                total_from_newsfeeds += 1
            elif install_metric.installed_via_unknown == True:
                total_from_unknown += 1
        
        self.response.out.write(simplejson.dumps({'status': 'ok', 'cursor': str(query.cursor()), 'total_users': total_users, 'total_from_ads': total_from_ads, 'total_from_newsfeeds': total_from_newsfeeds, 'total_from_unknown': total_from_unknown, 'count': len(install_metrics) }))

# Runs through the system and calculates the installation path for each user.  Batches 50 users at a time
class AdminInstallMetricCalculatorHandler(webapp.RequestHandler):
    def post(self):
        query = User.all()
        query.order('-created_at')
        cursor = self.request.get('cursor')
        if cursor != None:
            query.with_cursor(cursor)

        users = query.fetch(50)

        for user in users:
            page_view_with_user = PageView.gql("WHERE user = :1 ORDER BY created_at ASC", user).get() 
            
            if page_view_with_user == None:
                logging.error("Couldn't find PageView for User(key=%s,fb_user_id=%s)" % (str(user.key()) % str(user.fb_user_id)))
                page_view_with_user = PageView() # Fake it till we make it
            
            if page_view_with_user.session_id != None and len(page_view_with_user.session_id) > 0:
                page_view_with_session_id = PageView.gql("WHERE session_id = :1 ORDER BY created_at ASC", page_view_with_user.session_id).get()
            else:
                page_view_with_session_id = page_view_with_user
            
            installed_at = page_view_with_user.created_at
            if page_view_with_session_id.referrer == None or len(page_view_with_session_id.referrer) < 10:
                url_to_parse = page_view_with_session_id.url
            else:
                url_to_parse = page_view_with_session_id.referrer
            
            parsed_referral_url = urlparse(url_to_parse)
            params = cgi.parse_qs(parsed_referral_url.query)
            
            if 'suid' in params and params['suid'] != None and len(params['suid'][0]) > 0:
                installed_via_newsfeed = True
                referring_user = User.gql("WHERE __key__ = :1", db.Key(params['suid'][0])).get()
                newsfeed_search_term = '|'.join(params['q'])
                newsfeed_verb = '|'.join(params['v'])
                ad_name = None
                installed_via_ad = False
                installed_via_unknown = False
            elif 'q' in params and params['q'] != None and len(params['q'][0]) > 0:
                installed_via_newsfeed = False
                referring_user = None
                newsfeed_search_term = None
                newsfeed_verb = None
                ad_name = '|'.join(params['q'])
                installed_via_ad = True
                installed_via_unknown = False
            else:
                installed_via_newsfeed = False
                referring_user = None
                newsfeed_search_term = None
                newsfeed_verb = None
                ad_name = None
                installed_via_ad = False
                installed_via_unknown = True   
            
            install_metric = InstallMetric.gql("WHERE user = :1", user).get()
            if install_metric == None:
                install_metric = InstallMetric(
                    fb_user_id = user.fb_user_id,
                    user = user,
                    installed_at = installed_at,
                    installed_via_ad = installed_via_ad,
                    ad_name = ad_name,
                    installed_via_newsfeed = installed_via_newsfeed,
                    referring_user = referring_user,
                    newsfeed_search_term = newsfeed_search_term,
                    newsfeed_verb = newsfeed_verb,
                    installed_via_unknown = installed_via_unknown
                )
            else:    
                install_metric.fb_user_id = user.fb_user_id
                install_metric.user = user
                install_metric.installed_at = installed_at
                install_metric.installed_via_ad = installed_via_ad
                install_metric.ad_name = ad_name
                install_metric.installed_via_newsfeed = installed_via_newsfeed
                install_metric.referring_user = referring_user
                install_metric.newsfeed_search_term = newsfeed_search_term
                install_metric.newsfeed_verb = newsfeed_verb
                install_metric.installed_via_unknown = installed_via_unknown
                
            install_metric.put()

        self.response.out.write(simplejson.dumps({'status': 'ok', 'cursor': str(query.cursor()), 'count': len(users) }))
        