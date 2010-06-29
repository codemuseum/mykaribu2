from google.appengine.ext import webapp, blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import urlfetch
from django.utils import simplejson
from google.appengine.ext import db

from models.question import Question

import helpers as h
import urllib
import logging

def add_question(qtext, hint, img, handler):
    question = Question()
    cookies = h.get_default_cookies(handler)
    current_user = h.get_current_user(cookies)
    if current_user:
        question.user = current_user
    question.qtext = qtext
    question.hint = hint
    question.img = img
    question.status = 1
    question.put()
    return question


#  This is just docmentation of the original questions/images. these calls don't actually work
#  because the img needs to be a blob_info
#        add_question("What dessert do you like?","tasty things...",'dessert2.original.jpg', self)
#        add_question("What sports team do you like?",None,'sports.original.jpg', self)
#        add_question("What Sex & the City character do you like?",None,'satc2.original.jpg', self)
#        add_question("What vacation spot do you like?","some place nice...",'vacation3.original.jpg', self)
#        add_question("What pet do you like?","cute... strong...",'puppy-kitten.original.jpg', self)
#        add_question("What's the best big city?","a cool place...",'city.original.jpg', self)

class QuestionAdmin(webapp.RequestHandler):
    def get(self):
        c = h.context()
        query = Question.all()
        results = query.fetch(1000)
        for q in results:
            q.i = str(q.img.key())
            q.k = q.key()
        c['questions'] = results
        h.render_out(self, 'question_admin.tplt', c)
    def post(self):
        key_str = self.request.get('k')
        k = db.Key(key_str)
        db.delete(db.get(k))
        self.redirect("/qad?msg=deleted.")
        
class QuestionUploader(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        c = h.context()
        c['upload_url'] = blobstore.create_upload_url('/qup')
        h.render_out(self, 'question_uploader.tplt', c)
    def post(self):
        question_text = self.request.get("question")
        question_hint = self.request.get("hint")
        upload_files = self.get_uploads('image')
        blob_info = upload_files[0]
        ent = add_question(question_text, question_hint, blob_info, self)
        self.redirect('/qad')

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

class ResultsHandler(webapp.RequestHandler):
    def get(self):
        img_rows = 3
        
        c = h.context()
        query = self.request.get('q')
        force_quest = self.request.get('force_quest')
        
        if not query: query = "red"
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
        url3 = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q='\
               +ue_query+'&key='\
               +h.cfg['gs_api_key']
        rpcs = []
        
        rpc = urlfetch.create_rpc(10)
        urlfetch.make_fetch_call(rpc,url)
        rpcs.append(rpc)
        rpc = urlfetch.create_rpc(10)
        urlfetch.make_fetch_call(rpc,url2)
        rpcs.append(rpc)
        rpc = urlfetch.create_rpc(10)
        urlfetch.make_fetch_call(rpc,url3)
        rpcs.append(rpc)
        for rpc in rpcs:
            rpc.wait()
        result = rpcs[0].get_result()        
        result2 = rpcs[1].get_result()
        result_web = rpcs[2].get_result()
        
        o = simplejson.loads(result.content)
        o2 = simplejson.loads(result2.content)
        o_web = simplejson.loads(result_web.content)
        
        from print_r import print_r
        #c['content'] = print_r(o_web, False)
        c['ad'] = ""
        all_imgs = o['responseData']['results']+o2['responseData']['results']
        c['web_data'] = o_web['responseData']['results']
        
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

            # pick up the questions and images for the
            q = None
            if not force_quest:
                query = Question.all()
                results = query.fetch(1000)
                if len(results) > 0:
                    import random
                    q = random.choice(results)
                else: # Added this to prevent IndexError: list index out of range in development
                    q = Question()
            else:
                k = db.Key(force_quest)
                q = db.get(k)
            
            image_key = q.img.key() if q.img is not None else '' # Added to make development safe
            c['header_img'] = h.cfg['direct_url']+'/serve/'+str(image_key)
            c['header_txt'] = q.qtext
            c['hint'] = q.hint
            if not c['hint']:
                c['hint'] = "type something."
            c['search_form_display'] = "none"
        h.render_out(self, 'results.tplt', c)
