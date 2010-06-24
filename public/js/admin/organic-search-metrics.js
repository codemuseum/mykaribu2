var OrganicSearchMetrics = {
  statusEl: $('#status'),
  statusCount: 0,
  running: false,
  init: function() { 
      $("#calculate-button").click(function(ev) { OrganicSearchMetrics.calculateNow(); });
      this.fetchSummaryNow();
  },
  calculateDataLoop: function(cursor, callback) {
    OrganicSearchMetrics.statusEl.text(OrganicSearchMetrics.statusCount + "...");
    var cursorParam = cursor == null ? {} : {'cursor': cursor};
    $.post('/admin/organicsearchmetrics/calculator.json', cursorParam, function(data) {
			if (data['count'] == 0) { callback(); }
	        else {
				OrganicSearchMetrics.calculateDataLoop(data['cursor'], callback);
			}
	}, 'json');
  },
  calculateNow: function() { 
      if (this.running) return false;
      
      this.running = true;
      this.statusCount = 0;
      this.calculateDataLoop(null, function() {
        OrganicSearchMetrics.statusEl.text("DONE!");
        OrganicSearchMetrics.running = false;
        OrganicSearchMetrics.fetchSummaryNow();
      });
  }, 
  fetchSummaryNow: function() {
      $('#loading-msg').fadeIn(); 
      $('#total-users').text('...');
      $('#histogram-text').text('...');
      this.fetchSummaryLoop(null, {total_users: 0, results: {}} , function(data) {
          $('#total-users').text(data.total_users);
          var histogramHtmls = [];
          for (var key in data.results) {
              histogramHtmls.push('<li><span>Users with '+key+'</span><span>: '+data.results[key]+' ('+Math.round(100*data.results[key]/data.total_users)+'%)</span></li>');
          }
          histogramHtmls.sort();
          $('#histogram-text').html('<ul>'+histogramHtmls.join('').replace('_organic_searches', ' Organic Searches')+'</ul>');
      });
  },
  fetchSummaryLoop: function(cursor, currentData, callback) {
    var cursorParam = cursor == null ? {} : {'cursor': cursor};
    $.post(this.sourceUrl, cursorParam, function(data) {
			if (data['count'] == 0) { $('#loading-msg').fadeOut(); callback(currentData); }
      else {
          mergedData = {};
          mergedData.total_users = currentData.total_users + data.total_users;
          mergedData.results = currentData.results;
          for (var key in data.results) {
              if (mergedData.results[key] == null) { mergedData.results[key] = 0; }
              mergedData.results[key] += data.results[key];
          }
                
				OrganicSearchMetrics.fetchSummaryLoop(data['cursor'], mergedData, callback);
			}
	}, 'json');
  }
};
OrganicSearchMetrics.init();