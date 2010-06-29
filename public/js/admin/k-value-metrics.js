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
         chart.addRow([data.results[i].date, data.results[i].viral_signups/data.results[i].total_signups]); 
      }
      // Create and draw the visualization.
      new google.visualization.LineChart(document.getElementById('graph')).
        draw(chart, {curveType: "function", width: 500, height: 400, vAxis: {maxValue: 2}});
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
                
				KValueMetrics.fetchSummaryLoop(data['cursor'], mergedData, callback);
			}
	}, 'json');
  }
};
KValueMetrics.init();