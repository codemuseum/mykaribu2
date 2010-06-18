var Queries = {
    lastStoredQuery: null,
   init: function() {
       if ($('#results')[0]) {
          var query = $('#previous_q')[0].value;
          var privacy = $('#private_true')[0] ? $('#private_true')[0].checked : false;
          // Don't store the query if this id exists the first time around 
          if ($('#store_query').text() != 'false') { 
            this.storeQuery(query, privacy);
            // if (!privacy) { this.promptToCancelQueryShare(query); }
          } 
          // (but remove it so subsequent queries are picked up)
          else { $('#store_query').remove(); }
        }
   },
   storeQuery: function(query, privacy) {
     // TODO make this query have some protection against constant attack from another site (via javascript)
     this.lastStoredQuery = query;
     $.post('/storequeries.json', { q: query, p: privacy, referrer: document.referrer, u: document.location.href },  function(data) {
       if (data['status'] == 'error') {console.log("Error: "+data.toString()); } // ErrorLogger.report(data.toString()); }
       // if (data['current_user']) {Header.currentUserSearchScore(data['current_user']['user']['search_points']);}
     });
   },
    resultClick: function(a) {
     if (!this.lastStoredQuery) {return;}
     var resultBase = $(a);
     var resultUrl = resultBase.find('.raw-result-url').text();
     var resultImg = resultBase.find('img');
     var resultImgUrl = resultImg[0] ? resultImg[0].src : '';
	//$('body').ajaxError(function(a,b,c,d) {
	//    alert(b.status);
	//});
	$.post('/storeresultclicks.json',
	       {q: this.lastStoredQuery, u: (resultUrl && resultUrl != '' ? resultUrl : a.href), src: a.className, referrer: document.referrer, image_url: resultImgUrl },
	       function(data) {
		   if (data['status'] == 'error') { ErrorLogger.report(data.toString()); }
	       });

    }
};
Queries.init();
