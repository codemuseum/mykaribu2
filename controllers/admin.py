#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from django.utils import simplejson
import datetime

# *** Helpers
import helpers as h

# *** Models
from models.pageview import PageView
from models.query import Query
from models.resultview import ResultView
from models.user import User

# *** Handlers

class AdminHelper:
    @staticmethod
    def writePaginatedDataJson(handler, model, cursor_param=None):
        query = model.all()
        query.order('-created_at')
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
            if isinstance(val, basestring):
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
        h.output(self, "Admin: <a href='/admin/pageviews'>Page Views</a> | <a href='/admin/users'>Users</a>  | <a href='/admin/querys'>Searches</a> | <a href='/admin/resultviews'>Result Views</a> |  <a href='/admin/paths'>Navigation Paths</a> | <a href='/admin/url-analyzer'>URL Analyzer</a>")

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
                        
        
        
        
        