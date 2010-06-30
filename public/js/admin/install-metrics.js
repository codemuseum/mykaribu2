var InstallMetrics = {
  statusEl: $('#status'),
  statusCount: 0,
  running: false,
  init: function() { 
      $("#calculate-install-metrics-button").click(function(ev) { InstallMetrics.calculateNow(); });
      if ($('#auto-fetch-install-metrics')[0]) { this.fetchSummaryNow(); }
  },
  calculateDataLoop: function(cursor, callback) {
      InstallMetrics.statusCount++;
    InstallMetrics.statusEl.text(InstallMetrics.statusCount + "...");
    var cursorParam = cursor == null ? {} : {'cursor': cursor};
    $.post('/admin/installmetrics/calculator.json', cursorParam, function(data) {
			if (data['count'] == 0) { callback(); }
	        else {
				InstallMetrics.calculateDataLoop(data['cursor'], callback);
			}
	}, 'json');
  },
  calculateNow: function() { 
      if (this.running) return false;
      
      this.running = true;
      this.statusCount = 0;
      this.calculateDataLoop(null, function() {
        InstallMetrics.statusEl.text("DONE!");
        InstallMetrics.running = false;
        InstallMetrics.fetchSummaryNow();
      });
  },
  fetchSummaryNow: function() {
      $('#loading-msg').fadeIn(); 
      $('#total-users').text('...');
      $('#total-from-ads').text('...');
      $('#total-from-newsfeeds').text('...');
      $('#total-from-unknown').text('...');
      this.fetchSummaryLoop(null, {total_users: 0, total_from_ads: 0, total_from_newsfeeds: 0, total_from_unknown: 0} , function(data) {
          $('#total-users').text(data.total_users);
          $('#total-from-ads').text(data.total_from_ads + ' ('+Math.round(100*data.total_from_ads/data.total_users)+'%)');
          $('#total-from-newsfeeds').text(data.total_from_newsfeeds + ' ('+Math.round(100*data.total_from_newsfeeds/data.total_users)+'%)');
          $('#total-from-unknown').text(data.total_from_unknown + ' ('+Math.round(100*data.total_from_unknown/data.total_users)+'%)');
      });
  },
  fetchSummaryLoop: function(cursor, currentData, callback) {
    var cursorParam = cursor == null ? {} : {'cursor': cursor};
    $.post(null, cursorParam, function(data) {
			if (data['count'] == 0) { $('#loading-msg').fadeOut(); callback(currentData); }
	        else {
	            mergedData = {}
                for (var key in currentData) {  mergedData[key] = currentData[key] + data[key]; }
				InstallMetrics.fetchSummaryLoop(data['cursor'], mergedData, callback);
			}
	}, 'json');
  }
};
InstallMetrics.init();