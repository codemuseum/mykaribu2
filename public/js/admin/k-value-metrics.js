// This relies on all Install Metrics being Calculated already.
var KValueMetrics = {
  statusEl: $('#status'),
  statusCount: 0,
  running: false,
  graphReady: false,
  kValueDaySpan: 7,
  init: function() { 
      google.setOnLoadCallback(function() { KValueMetrics.graphReady = true; });
      google.load('visualization', '1', {packages: ['corechart']});
      
      $("#calculate-k-value-metrics-button").click(function(ev) { 
        InstallMetrics.running = true;
        InstallMetrics.calculateDataLoop(null, function() {
          InstallMetrics.running = false;
          KValueMetrics.calculateNow();
        });
      });
      if ($('#auto-fetch-k-value-metrics')[0]) { this.fetchSummaryNow(); }
  },
  clearDataLoop: function(cursor, callback) {
      KValueMetrics.statusCount++;
      KValueMetrics.statusEl.text(KValueMetrics.statusCount + " [clearing old k value metrics]...");
      var cursorParam = cursor == null ? {'span_in_days': this.kValueDaySpan} : {'cursor': cursor, 'span_in_days': this.kValueDaySpan};
      $.post('/admin/kvaluemetrics/clearer.json', cursorParam, function(data) {
  		if (data['count'] == 0) { callback(); }
          else {
              KValueMetrics.clearDataLoop(data['cursor'], callback);
          }
  	}, 'json');
      
  },
  calculateDataLoop: function(cursor, callback) {
      KValueMetrics.statusCount++;
    KValueMetrics.statusEl.text(KValueMetrics.statusCount + " [calculating k value metrics]...");
    var cursorParam = cursor == null ? {'span_in_days': this.kValueDaySpan} : {'cursor': cursor,'span_in_days': this.kValueDaySpan};
    $.post('/admin/kvaluemetrics/calculator.json', cursorParam, function(data) {
		if (data['count'] == 0) { callback(); }
        else {
            KValueMetrics.calculateDataLoop(data['cursor'], callback);
        }
	}, 'json');
  },
  calculateNow: function() { 
      if (this.running) return false;
      
      this.running = true;
      this.statusCount = 0;
      
      this.clearDataLoop(null, function() {
        KValueMetrics.statusEl.text("Completed clearing old k values... still working...");
        KValueMetrics.calculateDataLoop(null, function() {
          KValueMetrics.statusEl.text("DONE!");
          KValueMetrics.running = false;
          KValueMetrics.fetchSummaryNow();
        });
      });
  }, 
  fetchSummaryNow: function() {
      $('#loading-msg').fadeIn(); 
      $('#graph').text('...');
      this.fetchSummaryLoop(null, {results: []} , function(data) {
          KValueMetrics.displayGraph(data);
      });
  },
  displayGraph: function(data) {
      var maxK = 0;
        this.statusEl.text("Starting to build graph.");
      if (!this.graphReady) { 
          this.statusEl.text("Google Chart Not Loaded Yet, trying in 5 seconds"); 
          setTimeout(function(){KValueMetrics.displayGraph(data);},5000); 
          return false;
      }
      var chart = new google.visualization.DataTable();
      chart.addColumn('date', 'x');
      chart.addColumn('number', '7-Day K Value');
      for (var i in data.results) { 
          var k = data.results[i].viral_signups/data.results[i].total_signups;
          var date = new Date(data.results[i].date);
          if (k > maxK) maxK = k;
          if (date <= new Date()) chart.addRow([date, k]); 
      }
      // Create and draw the visualization.
      new google.visualization.LineChart(document.getElementById('graph')).
        draw(chart, {curveType: "function", width: $(window).width() - 20, height: $(window).height() - 60, vAxis: {maxValue: maxK}});
  },
  fetchSummaryLoop: function(cursor, currentData, callback) {
    var cursorParam = cursor == null ? {} : {'cursor': cursor};
    $.post(this.sourceUrl, cursorParam, function(data) {
			if (data['count'] == 0) { $('#loading-msg').fadeOut(); callback(currentData); }
      else {
          mergedData = {};
          mergedData.results = currentData.results.concat(data.results);
				KValueMetrics.fetchSummaryLoop(data['cursor'], mergedData, callback);
			}
	}, 'json');
  },
  test: function() {
      var d = {"status": "ok", "cursor": "E9oBYG1haW5ta2RldgBLVmFsdWVNZXRyaWMAdXBkYXRlZF9hdAB3Aft1x6bh9_t_bWFpbm1rZGV2AIuSS1ZhbHVlTWV0cmljAJj5RoyMgIuSS1ZhbHVlTWV0cmljAJj5RoyMgOABABQ=", "results": [{"total_signups": "135", "updated_at": "2010-06-30 05:11:08.933103", "span_in_days": "7", "date": "2010-06-24", "viral_signups": "5", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxi9yQIM"}, {"total_signups": "122", "updated_at": "2010-06-30 05:11:08.796997", "span_in_days": "7", "date": "2010-06-23", "viral_signups": "5", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxi2wwQM"}, {"total_signups": "97", "updated_at": "2010-06-30 05:11:08.745855", "span_in_days": "7", "date": "2010-06-22", "viral_signups": "4", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxj5hAQM"}, {"total_signups": "73", "updated_at": "2010-06-30 05:11:08.693960", "span_in_days": "7", "date": "2010-06-21", "viral_signups": "4", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxjExgMM"}, {"total_signups": "42", "updated_at": "2010-06-30 05:11:08.648696", "span_in_days": "7", "date": "2010-06-20", "viral_signups": "1", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxiF1gMM"}, {"total_signups": "8", "updated_at": "2010-06-30 05:11:08.598397", "span_in_days": "7", "date": "2010-06-19", "viral_signups": "None", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxjLmgIM"}, {"total_signups": "4", "updated_at": "2010-06-30 05:11:08.559475", "span_in_days": "7", "date": "2010-06-18", "viral_signups": "None", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxj2igIM"}, {"total_signups": "150", "updated_at": "2010-06-30 05:11:07.484773", "span_in_days": "7", "date": "2010-06-25", "viral_signups": "7", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxiEjgEM"}, {"total_signups": "167", "updated_at": "2010-06-30 05:11:05.930608", "span_in_days": "7", "date": "2010-06-26", "viral_signups": "11", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxjYxAEM"}, {"total_signups": "146", "updated_at": "2010-06-30 05:10:40.089144", "span_in_days": "7", "date": "2010-06-27", "viral_signups": "12", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxiU3AEM"}, {"total_signups": "115", "updated_at": "2010-06-30 05:10:18.767937", "span_in_days": "7", "date": "2010-06-28", "viral_signups": "9", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxjKmgIM"}, {"total_signups": "158", "updated_at": "2010-06-30 05:10:03.096809", "span_in_days": "7", "date": "2010-06-29", "viral_signups": "17", "__key__": "agltYWlubWtkZXZyEwsSDEtWYWx1ZU1ldHJpYxiydgw"}, {"total_signups": "167", "updated_at": "2010-06-30 05:09:52.042894", "span_in_days": "7", "date": "2010-06-30", "viral_signups": "17", "__key__": "agltYWlubWtkZXZyEwsSDEtWYWx1ZU1ldHJpYxixdgw"}, {"total_signups": "154", "updated_at": "2010-06-30 05:09:45.036638", "span_in_days": "7", "date": "2010-07-01", "viral_signups": "17", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxj2qwQM"}, {"total_signups": "135", "updated_at": "2010-06-30 05:09:32.286466", "span_in_days": "7", "date": "2010-07-02", "viral_signups": "15", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxjnkgIM"}, {"total_signups": "114", "updated_at": "2010-06-30 05:09:21.625817", "span_in_days": "7", "date": "2010-07-03", "viral_signups": "11", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxiE1gMM"}, {"total_signups": "101", "updated_at": "2010-06-30 05:09:14.887822", "span_in_days": "7", "date": "2010-07-05", "viral_signups": "9", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxi-lwMM"}, {"total_signups": "101", "updated_at": "2010-06-30 05:09:14.836241", "span_in_days": "7", "date": "2010-07-04", "viral_signups": "9", "__key__": "agltYWlubWtkZXZyEwsSDEtWYWx1ZU1ldHJpYxj8GAw"}, {"total_signups": "34", "updated_at": "2010-06-30 05:08:44.784763", "span_in_days": "7", "date": "2010-07-06", "viral_signups": "1", "__key__": "agltYWlubWtkZXZyFAsSDEtWYWx1ZU1ldHJpYxiDjgEM"}], "count": 19};
            $('#graph').text('...');
            KValueMetrics.displayGraph(d);
  }
};
KValueMetrics.init();