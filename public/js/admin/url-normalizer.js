var UrlNormalizer = {
  filterParamsInput: $('#filtered-params')[0],
  statusEl: $('#status'),
  statusCount: 0,
  running: false,
  init: function() { 
      $("#normalize-button").click(function(ev) { UrlNormalizer.normalizeNow(); });
  },
  fetchDataLoop: function(cursor, filteredParams, callback) {
    UrlNormalizer.statusEl.text(UrlNormalizer.statusCount + "...");
    var cursorParam = cursor == null ? {filtered_params: filteredParams} : {'cursor': cursor, filtered_params: filteredParams};
    $.post('/admin/pageviews/normalizer', cursorParam, function(data) {
			if (data['count'] == 0) { callback(); }
	        else {
				UrlNormalizer.fetchDataLoop(data['cursor'], filteredParams, callback);
			}
	}, 'json');
  },
  normalizeNow: function() { 
      if (this.running) return false;
      
      this.running = true;
      this.statusCount = 0;
      this.fetchDataLoop(null, this.filterParamsInput.value, function() {
        UrlNormalizer.statusEl.text("DONE!");
        UrlNormalizer.running = false;
      });
  }
};
UrlNormalizer.init();