var UrlAnalyzer =  {
	currentUrl: null,
	currentDoubleCount: null,
	init: function() {
		$("#url-input").autocomplete("/admin/url-suggest", { selectFirst: true });
		$('#double-count').change(function(ev) { UrlAnalyzer.loadUrl(); });
	},
	loadUrl: function() {
		var loadingHtml = '<div class="loading"><img src="http://bzz.heroku.com/images/loading.gif"/> Loading...</div>';
		this.currentUrl = $('#url-input')[0].value;
		this.currentDoubleCount = $('#double-count')[0].checked ? true : false;
		
		$('#page').html('<div class="u">'+this.currentUrl + '</div><div id="page-stats" class="stats">'+loadingHtml+'</div>');
		$('#entrances').html(loadingHtml);
		$('#exits').html(loadingHtml);
		
		this.fetchAndMergePageStats(this.currentUrl, this.currentDoubleCount, 0, {results: [], total_pageviews:0, total_sessions:0 }, function(data) {
			$('#page-stats').html('<div>Hits: '+data['total_pageviews']+' / from ' + data['total_sessions'] + ' Sessions</div');
		});
		this.fetchAndMergeFunnelStats('entrances', this.currentUrl, this.currentDoubleCount, 0, {results: {}, total_entrance_pageviews: 0, total_entrances: 0}, function(data) {
			$('#entrances').html(UrlAnalyzer.funnelResultsHtml(data, 'entrance'));
		});
		this.fetchAndMergeFunnelStats('exits', this.currentUrl, this.currentDoubleCount, 0, {results: {}, total_entrance_pageviews: 0, total_entrances: 0}, function(data) {
			$('#exits').html(UrlAnalyzer.funnelResultsHtml(data, 'exit'));
		});
	},
	funnelUrlHtml: function(url, count, totalCount, mode) {
		return '<div class="'+mode+'"><div class="u">'+url+'</div><div class="stats">'+Math.round(count * 100 / totalCount)+'%, '+count+'/'+totalCount+'</div></div>';
	},
	funnelResultsHtml: function(data, mode) {
	
		if (data['total_entrances'] == 0) {
			return "<div class='none'>[none]</div>";
		}
		else {
			var resultsArry = [];
			for (var k in data['results']) {
				var res = [data['results'][k], UrlAnalyzer.funnelUrlHtml(k, data['results'][k], data['total_entrance_pageviews'], mode)];
				resultsArry.push(res);
			}
			resultsArry.sort(function(a,b) { return a[0] - b[0]; });
			resultsArry.reverse();
			return $.map(resultsArry, function(v,i) { return v[1]; }).join('\n');
		}
	},
	fetchAndMergePageStats: function(pageUrl, doubleCount, pageNum, currentData, callback) {
		$.getJSON('/admin/urls/stats.json', {url: pageUrl, double_count_sessions: doubleCount, page: pageNum}, function(data) {
			if (data['total_pageviews'] == 0) {
				// Loop through and calculate the real values
				currentData['total_pageviews'] = 0;
				// Iterate over sessions and add up the pageview counts for each
				for (var sessId in currentData['results']) { currentData['total_pageviews'] += currentData['results'][sessId]; }
				
				currentData['total_sessions'] = 0;
				// Iterate over sessions and add them up
				for (var sessId in currentData['results']) { if (currentData['results'][sessId] > 0) { currentData['total_sessions'] += 1; } }
				
				callback(currentData);
			}
			else {
				mergedData = currentData;
				for (var sessId in data['results']) {
					if (! (mergedData['results'][sessId] > 0)) { // init hash if necessary
						mergedData['results'][sessId] = 0;
					}
					mergedData['results'][sessId] += data['results'][sessId];
				}
			
				UrlAnalyzer.fetchAndMergePageStats(pageUrl, doubleCount, pageNum + 1, mergedData, callback);
			}
		});
	},
	fetchAndMergeFunnelStats: function(modeStr, pageUrl, doubleCount, pageNum, currentData, callback) {
		$.getJSON('/admin/urls/funnel.json', {mode: modeStr, url: pageUrl, double_count_sessions: doubleCount, page: pageNum}, function(data) {
			if (data['total_entrances'] == 0) {
				// Loop through and calculate the final values
				currentData['total_entrance_pageviews'] = 0;
				// Iterate over entrances and add up the pageview counts for each
				for (var entr in currentData['results']) { currentData['total_entrance_pageviews'] += currentData['results'][entr]; }
				
				currentData['total_entrances'] = 0;
				// Iterate over entrances and add them up
				for (var entr in currentData['results']) { if (currentData['results'][entr] > 0) { currentData['total_entrances'] += 1; } }

				callback(currentData);
			}
			else {
				mergedData = currentData;
				for (var entr in data['results']) {
					if (! (mergedData['results'][entr] > 0)) { // init hash if necessary
						mergedData['results'][entr] = 0;
					}
					mergedData['results'][entr] += data['results'][entr];
				}
			
				UrlAnalyzer.fetchAndMergeFunnelStats(modeStr, pageUrl, doubleCount, pageNum + 1, mergedData, callback);
			}
		});
	}
};
UrlAnalyzer.init();