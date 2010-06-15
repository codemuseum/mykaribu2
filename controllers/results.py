from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from django.utils import simplejson
import helpers as h
import urllib

class MultiFetch():
    def add_fetch(self, url):
        self.outstanding[url] = ""
        
class ResultsHandler(webapp.RequestHandler):
    def get(self):
        img_rows = 2
        
        c = h.context()
        query = self.request.get('q')
        c['query'] = query

        # fetch the google image results
        ue_query = urllib.quote_plus(query)
        c['ue_query'] = ue_query
        url = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&rsz=large&q='\
               +ue_query+'&key='\
               +h.cfg['gs_api_key']
        url2 = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&rsz=large&start=8&q='\
               +ue_query+'&key='\
               +h.cfg['gs_api_key']
        result = urlfetch.fetch(url)
        result2 = urlfetch.fetch(url2) # need to put these into an async fetch
        o = simplejson.loads(result.content)
        o2 = simplejson.loads(result.content)
        
        from print_r import print_r
        c['content'] = print_r(o, False)
        c['ad'] = ""
        all_imgs = o['responseData']['results']+o2['responseData']['results']

        # calculate appropriate sizes for image placement
        c['max_height'] = int(max(all_imgs, key=lambda x: int(x['tbHeight']))['tbHeight'])
        c['row_height'] = c['max_height']+20

        # borders to make all the img divs the same size
        for i in all_imgs:
            i['bot_border'] = (c['row_height']-int(i['tbHeight']))/2
            i['top_border'] = c['row_height']-int(i['tbHeight'])-i['bot_border']
            i['right_margin'] = 5

        # init loop variables
        c['mini_imgs'] = list()
        start_img = 0
        curr_img = 0
        done = False

        # begin the super ugly loop to generate rows
        while not done:
            taken_px = 0
            row_done = False
            num_imgs = 0
            # figure out how many images we can place in the row given the normal size
            while not row_done:
                additional_px = 0
                additional_px += 20 # min right & left border
                additional_px += int(all_imgs[curr_img]['tbWidth']) # image itself
                if taken_px+additional_px > 758:
                    row_done = True
                    #done = True
                    num_imgs = curr_img - start_img
                else:
                    additional_px += 5 # white margin between images (the last one doesn't have it)
                    taken_px += additional_px
                    curr_img += 1
                if curr_img >= len(all_imgs):
                    num_imgs = curr_img - start_img
                    row_done = True
                    done = True

            # now take all the remaining space and distribute it to the borders of the images
            remaining_space  = 758-taken_px
            border_px = int(remaining_space/(num_imgs*2)+10)
            remainder = remaining_space-(border_px-10)*2*num_imgs

            row_imgs = all_imgs[start_img:start_img+num_imgs]
            
            # hand out the border px to the images and get rid of the remainder (also add the index)
            for i in row_imgs:
                i['left_border'] = border_px
                if(remainder > 0):
                    i['left_border'] += 1
                    remainder -= 1
                i['right_border'] = border_px
                if(remainder > 0):
                    i['right_border'] += 1
                    remainder -= 1
            
            c['num_imgs'] = num_imgs

            # set the last img in a row to have no 5px margin
            row_imgs[len(row_imgs)-1]['right_margin'] = 0

            c['mini_imgs'].append(row_imgs)
            if len(c['mini_imgs']) >= img_rows: done = True

            start_img += num_imgs
        
        h.render_out(self, 'results.tplt', c)