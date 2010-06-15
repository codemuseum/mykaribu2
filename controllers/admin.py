#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from django.utils import simplejson

# *** Helpers
import helpers as h

# *** Models
from models.pageview import PageView

# *** Handlers

# Admin main handler
class AdminHandler(webapp.RequestHandler):
	def get(self):
		h.output(self, "Admin: <a href='/admin/pageviews'>Page Views</a> | <a href='/admin/paths'>Navigation Paths</a> | <a href='/admin/url-analyzer'>URL Analyzer</a>")

class AdminPageViewsHandler(webapp.RequestHandler):
	def get(self):
		page_views = db.GqlQuery("SELECT * FROM PageView ORDER BY created_at DESC")
		result = ''
		for page_view in page_views:
			result += "<tr><td>"+str(page_view.session_order)+"</td><td>"+page_view.normalized_url+"</td><td>"+page_view.url+"</td><td>"+page_view.referrer+"</td><td>"+page_view.session_id+"</td><td>"+page_view.ip_address+"</td><td>"+str(page_view.created_at)+"</td><td>"+str(page_view.user_id)+"</td></tr>"

		h.output(self, '<html><head><style>tr:hover {background-color:#ccc;}th{background-color:#000;color:#fff;}table{width:100%}</style></head><body>Page Views:<table border="1"><tr><th>Order</th><th>Normalized URL</th><th>URL</th><th>Referrer</th><th>Session ID</th><th>IP Address</th><th>Created At</th><th>User ID</th></tr>'+result+'</table></body></html>')


class AdminPathsHandler(webapp.RequestHandler):
	def get(self):
		h.output(self, '<html><head><style>.end{background-color:#f1f1f1; color:#555; font-size:8px; font-weight:bold;}.path {padding:10px;border-bottom:1px dashed #ccc;margin-top:5px;} .path:hover {background-color:#ddd;}.path a {cursor:pointer;color:#383838;text-decoration:none}.path a:hover{text-decoration:underline}.clear{float:none;clear:both;height:1px}.percent{float:left;width:4%;padding-left:1%;}.numeric{float:left;width:4%;padding-left:1%;}.url{float:left;width:89%;padding-left:1%}.sub-paths{margin-left:2%; border-left:1px solid #ccc;padding-left:10px;} .path.collapsed .sub-paths {display:none}</style></head><body>Paths:<div id="paths"></div><script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js" type="text/javascript"></script><script src="/public/javascripts/admin/paths.js" type="text/javascript"></script></body></html>')
		

class AdminPathDataHandler(webapp.RequestHandler):
	def get(self):
		session_ids = None
		query = PageView.all()
		query.order('-created_at')
		query.filter('session_order =', int(self.request.get('session_order')))
		if self.request.get('session_ids') != '':
			query.filter('session_id IN', simplejson.loads(self.request.get('session_ids')))

		page_views = query.fetch(1000, int(self.request.get('session_order_offset')) * 1000)
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
		
		self.response.out.write(simplejson.dumps({'status': 'ok', 'results': collapsed_page_views, 'total_pageviews_in_query': len(page_views) }))


class AdminUrlAnalyzerHandler(webapp.RequestHandler):
	def get(self):
		h.output(self, '<html><head><link rel="stylesheet" href="/public/stylesheets/jquery.autocomplete.css" type="text/css" /><style>.loading{font-size:83%; color:#92ABC2;padding:10px}#url-input {width:80%} .stats {font-size:83%; color:#999; padding:8px} .button {padding:3px 7px; background-color:#999; border:1px solid #333; cursor:pointer; color:#fff;}.url {padding-bottom:20px;} #analyzer {position:relative;} #entrances-arrow{top:47%;left:30%; width:64px; height:64px; position:absolute;} #exits-arrow{top:47%;left:61%; width:64px; height:64px; position:absolute;} #entrances, #page, #exits {width:30%; border:1px solid #eee; float:left; height:90%; display:table-cell; vertical-align:middle;margin-left:1%;overflow:auto} #page {text-align:center; line-height:100%; height:50%; padding-top:20%;-moz-box-shadow:5px 5px 5px #ccc;box-shadow: 5px 5px 5px #ccc;-webkit-box-shadow: 5px 5px 5px #ccc; }#entrances {text-align:right}.entrance, .exit {border-bottom:1px dashed #ccc; padding:10px} .entrance:nth-child(odd), .exit:nth-child(odd){background-color:#F5FAFF}</style></head><body><div class="url">URL: <input type="text" name="url" id="url-input" autocomplete="off" /> <a onclick="UrlAnalyzer.loadUrl();" class="button">Lookup</a><br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="checkbox" name="double_count" id="double-count" checked disabled="true" /> <label for="double-count">Allow Double-Counting of this URL in a Single Session</label></div><div id="analyzer"><div id="entrances-arrow"><img src="/public/images/admin/gray-right-arrow.png" width="64"/></div><div id="exits-arrow"><img src="/public/images/admin/gray-right-arrow.png" width="64"/></div><div id="entrances"></div><div id="page"></div><div id="exits"></div><div style="clear:both"></div></div><script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js" type="text/javascript"></script><script src="/public/javascripts/jquery.autocomplete.min.js" type="text/javascript"></script><script src="/public/javascripts/admin/url-analyzer.js" type="text/javascript"></script></body></html>')

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
	def get(self):
		url = self.request.get('url')
		query = PageView.all()
		query.order('session_id')
		query.filter('normalized_url =', url)
		page_views = query.fetch(1000, int(self.request.get('page')) * 1000)
		
		page_views_by_session_id = {}
		for page_view in page_views: 
			if page_view.session_id in page_views_by_session_id:
				page_views_by_session_id[page_view.session_id] += 1
			else:
				page_views_by_session_id[page_view.session_id] = 1
		
		self.response.out.write(simplejson.dumps({'status': 'ok', 'results': page_views_by_session_id, 'total_pageviews': len(page_views), 'total_sessions': len(page_views_by_session_id.keys()) }))
		
class AdminUrlFunnelHandler(webapp.RequestHandler):
	def get(self):
		mode = self.request.get('mode')
		if mode == 'entrances':
			mode_session_order_add_amount = -1
		else:
			mode_session_order_add_amount =  1
		url = self.request.get('url')
		query = PageView.all()
		query.order('session_id')
		query.filter('normalized_url =', url)
		page_views = query.fetch(1000, int(self.request.get('page')) * 1000)
		
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
						
		
		self.response.out.write(simplejson.dumps({'status': 'ok', 'mode': mode, 'results': entrances_hash, 'total_entrances': len(entrances_hash.keys()), 'total_entrance_pageviews': sum(entrances_hash.values()) }))
						
		
		
		
		