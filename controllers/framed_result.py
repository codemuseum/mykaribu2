from google.appengine.ext import webapp
import helpers as h

class FramedResultHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        c['url'] = self.request.get("u")
        c['query'] = self.request.get("q")
        c['start'] = self.request.get("start")
        in_fb = self.request.get("infb").lower() == "true";
        c['was_in_facebook'] = in_fb
        c['this_result_url'] = self.request.url
        c['next_href_root'] = "http://next_href_root"
        curr_base_url = ( h.cfg["direct_url"], h.cfg["fb_url"] )[in_fb]
        c['back_to_results_href'] = curr_base_url + "/results?q=" + c['query'] + "&start=" + c['start']
        c['next_step_href'] = curr_base_url
        h.render_out(self, 'framed_result.tplt', c)

from google.appengine.api import urlfetch

class ShareCountsHandler(webapp.RequestHandler):
    def get(self):
        u = self.request.get("urls[]")
        url = "http://api.facebook.com/restserver.php?method=links.getStats&format=json&urls="+u
        result = urlfetch.fetch(url)
        self.response.headers['Content-Type'] = "application/json"
        h.output(self, result.content)
