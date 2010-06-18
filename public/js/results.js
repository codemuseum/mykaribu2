var Results = {
  SHARE_COUNTDOWN_FROM: 15,
  googleCseKey: $('#data-gcsek').text(),
  queryToCancel: null,
  queryShareCountdown: null,
  countdownTimer: null,
  lastStoredQuery: null,
  init: function() {
    if ($('#results')[0]) {
      var query = $('#previous_q')[0].value;
      var privacy = $('#private_true')[0] ? $('#private_true')[0].checked : false;
      // Don't store the query if this id exists the first time around
      if ($('#store_query').text() != 'false') { 
        this.storeQuery(query, privacy);
        if (!privacy) {
          this.promptToCancelQueryShare(query);
        }
      } 
      // (but remove it so subsequent queries are picked up)
      else { $('#store_query').remove(); }

      this.fetchShareCounts();
      this.fetchSearchResultImages(query);
    }
  },
  storeQuery: function(query, privacy) {
    // TODO make this query have some protection against constant attack from another site (via javascript)
    this.lastStoredQuery = query;
    $.post('/query_stores.json', { q: query, p: privacy, referrer: document.referrer, query_url: document.location.href },  function(data) {
      if (data['status'] == 'error') { ErrorLogger.report(data.toString()); }
      if (data['current_user']) {Header.currentUserSearchScore(data['current_user']['user']['search_points']);}
    });
  },
  promptToCancelQueryShare: function(query) {
    this.queryToCancel = query;
    this.queryShareCountdown = this.SHARE_COUNTDOWN_FROM;
    $('#sharing-notice').fadeIn(function() {
      Results.countdownTimer = setTimeout(function() {Results.decrementShareCountdown();}, 1000);
    });
  },
  decrementShareCountdown: function() {
    this.queryShareCountdown--;
    $('#sharing-notice-seconds').html(this.queryShareCountdown);
    if (this.queryShareCountdown == 0) {
      this.countdownTimer = null;
      $('#sharing-notice').fadeOut();
    }
    else {
      this.countdownTimer = setTimeout(function() {Results.decrementShareCountdown();}, 1000);
    }
  },
  cancelQueryShare: function() {
    if (this.countdownTimer) { clearTimeout(this.countdownTimer); this.countdownTimer = null; }

    $.post('/query_stores/cancel_share.json', {q: Results.queryToCancel}, function(data) {
      if (data['status'] == 'error') { ErrorLogger.report(data.toString()); }
    });
    $('#sharing-notice-seconds').html('cancelled');

    setTimeout(function() { $('#sharing-notice').fadeOut(); }, 1500);
  },
  fetchShareCounts: function() {
    // batch request all facebook counts
    var resultUrls = [];
    $('.raw-result-url').each(function(i) { resultUrls.push(encodeURI($(this).text())); });
    $.get('/share_counts?&urls[]=' + resultUrls.join(','), function(data) {
      Results.populateShareCounts(data);
    });
  },
  populateShareCounts: function(data) {
    $('.cse-result').each(function(i) {
      var result = $(this);
      var rawUrl = result.find('.raw-result-url').text();
      for (j in data) {
        if (data[j]['url'] == rawUrl) {
          Results.populateShareCount(result.find('.fb-share-count'), data[j]['total_count']);
          break;
        }
      }
    });
  },
  populateShareCount: function(div, num) {
    var text = num;
    if(num >= 1000000) text = Math.round(num/100000)/10+"M";
    else if(num >= 1000) text = Math.round(num/1000)+"K";
    div.html(text);
  },
  resultClick: function(a) {
    if (!this.lastStoredQuery) {return;}
    var resultUrl = $(a).parents('.cse-result').find('.raw-result-url').text();
    $.post('/results/result_click.json', {q: this.lastStoredQuery, url: (resultUrl && resultUrl != '' ? resultUrl : a.href), src: a.className}, function(data) {
      if (data['status'] == 'error') { ErrorLogger.report(data.toString()); }
    });
  },
  // Expects shareData to be has in format that fetchShareData returns, which can optionally have a {more: } object
  fbShare: function(url, shareData) {
    if (shareData == null) { this.fetchShareData('', url, function(data) { Results.fbShare(url, data); }); return false; }

    FB.ui({
      method: 'stream.publish',
      message: '',
      attachment: {
        name: shareData.name ? shareData.name : 'Search Result',
        description: shareData.description ? shareData.description : 'Click to read more!',
        href: url,
        media: [{ 'type': 'image', 'src': shareData.img ? shareData.img : 'http://blogs.trb.com/community/news/fort_lauderdale/forum/facebook_logo.png', 'href': url}]		    
      },
      action_links: [{ text: 'MORE STUFF', href: (shareData.more ? shareData.more : 'http://bzz.heroku.com/') }],
      user_prompt_message: 'Tell your friends what you found'
    }, 
    function(resp) { Results.fbShareComplete(url, resp); });

    $.post('/page_views.json', { u: '/fb-share-initiated?u='+url,  referrer: document.location.href }, function(data) {
      if (data['status'] == 'error') { ErrorLogger.report(data.toString()); }
    });
  },
  fbShareComplete:function(url, resp) {
    if (resp && resp.post_id) {
      $.post('/page_views.json', {
        u: '/fb-share-completed?u='+url+'&'+'post_id='+resp.post_id, 
        referrer: document.location.href
      }, function(data) {
        if (data['status'] == 'error') { ErrorLogger.report(data.toString()); }
      });
    }
  },
  fbShareWithFetch: function(baseUrl, shareUrl) {
    this.fetchShareData('', baseUrl, function(data) { Results.fbShare(shareUrl, data); });
  },
  // returns a hash to the callback of the data from google search {img: , name: , description: }
  fetchShareData: function(query, site, callback) {
    var base = 'http://ajax.googleapis.com/ajax/services/search';
    var result = {img: null, name: null, description: null};
    var imgReturned = false;
    var searchReturned = false;

    var imgBase = base + "/images?v=1.0&rsz=small&start=0&key="+encodeURI(Results.googleCseKey);
    $.getJSON(imgBase+"&q="+encodeURI(query+" site:"+site)+"&callback=?", function(data) {
      try {
        result.img = data.responseData.results[0].unescapedUrl;
      } 
      catch(ignored) {}
      imgReturned = true;
      if (searchReturned) {callback(result);}
    });

    var searchBase = base + "/web?v=1.0&rsz=small&start=0&key="+encodeURI(Results.googleCseKey);
    $.getJSON(searchBase+"&q="+encodeURI(query+" site:"+site)+"&callback=?", function(data) {
      try {
        result.description = data.responseData.results[0].content;
        result.name = data.responseData.results[0].titleNoFormatting;
      } 
      catch(ignored) {}
      searchReturned = true;
      if (imgReturned) {callback(result);}
    });
  },
  fetchSearchResultImages: function(query) {
    var base = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q="+encodeURI(query)+"&rsz=large&start=0&key="+encodeURI(Results.googleCseKey)+"&callback=?";
    $.getJSON(base, function(data) {
      var maxHeight = 0;
      var usedWidth = 0;
      var lastImg = 0;
      var widthStr = "";
      var dataLen = data.responseData.results.length;

      // first loop through and determine how many images we can fit and
      // how much space they take up (along with their white margins).
      for(var i = 0; i < dataLen; ++i) { 
        res = data.responseData.results[i];
        if(i > 0) currMargin = 5; 
        else currMargin = 0;
        newWidth = usedWidth + (parseInt(res.tbWidth)) + currMargin;
        widthStr += res.tbWidth+" ";

        if (newWidth >= 760) {
          numImg = i;
          break;
        }
        else usedWidth = newWidth;
      }

      // now loop through and drop the images we want along with their links
      for(var i = 0; i < numImg; ++i) {
        res = data.responseData.results[i];
        $('#gimg'+i).attr('src',res.tbUrl);
        $('#ga'+i).attr('href',"http://bzz.heroku.com/facebook/results?u="+res.originalContextUrl+"&q="+encodeURI(query)+"&start=0&infb=true");
        maxHeight = Math.max(res.tbHeight, maxHeight);
      }

      // calculate the grey padding 'matte' needed
      totalPadding = 760-usedWidth ; //-(5*(numImg-1));
      newPadding = Math.floor(totalPadding/(numImg*2));
      remnantPadding = totalPadding-newPadding*numImg*2;
      padArray = new Array();
      for (var i = 0; i < numImg*2; ++i) { padArray.push(newPadding); }
      i=0;
      while (remnantPadding) {
        padArray[i]++;
        remnantPadding--;
        i++;
      }

      // finally, loop through and distribute the padding
      for(var i = 0; i < numImg; ++i) {
        res = data.responseData.results[i];
        $('#gdiv'+i).css('height',maxHeight+20);
        $('#gimg'+i).css('top',(maxHeight-res.tbHeight)/2+10);
        if(i == numImg-1) newMargin = 0; else newMargin = 5;
        $('#gdiv'+i).css({'margin':'0px '+newMargin+'px 5px 0px','padding':'0px '+padArray[i*2]+'px 0px '+padArray[i*2+1]+'px'});
      }
    });
  }
};
Results.init();

var ErrorLogger = {
  report: function(msg) {
    $.post('/loggings.json', {log: msg});
  }
};

