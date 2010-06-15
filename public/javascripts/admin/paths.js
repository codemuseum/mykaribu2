var AdminPaths = {
	init: function() {
		var startAtSessionOrder = 0;
		this.fetchAndMergeData(startAtSessionOrder, 0, '', {total_pageviews_in_query:0, results: []}, function(data) {
			$('#paths').html(AdminPaths.pathResultsHtml(data, startAtSessionOrder));
			AdminPaths.bindPaths($('#paths .path'));
		});
	},
	fetchAndMergeData: function(sessionOrder, sessionOrderOffset, sessionIds, currentData, callbackForMergedData) {
		$.getJSON('/admin/paths/data.json', {session_order: sessionOrder, session_order_offset: sessionOrderOffset, session_ids: sessionIds}, function(data) {
			if (data['total_pageviews_in_query'] == 0) {
				currentData['results'].sort(function(a,b) { return a['count'] - b['count']; });
				currentData['results'].reverse();
				callbackForMergedData(currentData);
			}
			else {
				mergedData = {};
				mergedData['total_pageviews_in_query'] = data['total_pageviews_in_query'] + currentData['total_pageviews_in_query'];
				mergedData['results'] = currentData['results'];
				// sew up any duplicates between the two sets, and then tack on everything else
				for (var i in data['results']) {
					for (var j in mergedData['results']) {
						if (data['results'][i]['url'] == mergedData['results'][j]['url']) {
							mergedData['results'][j]['count'] += data['results'][i]['count'];
							mergedData['results'][j]['session_ids'] += data['results'][i]['session_ids'];
							data['results'][i] = null;
						}
					}
				}
				// remove any null (merged) results from data
				mergedData['results'] = mergedData['results'].concat($.grep(data['results'], function (a) { return a != null; }));
				AdminPaths.fetchAndMergeData(sessionOrder, sessionOrderOffset + 1, sessionIds, mergedData, callbackForMergedData);
			}
		});
	},
	pathHtml: function(path, totalCount, currentOrder) {
		return "<div class='path collapsed'><div class='data-path-url' style='display:none'>"+path['url']+"</div><div class='data-path-order' style='display:none'>"+currentOrder+"</div><div class='data-session-ids' style='display:none'>[\""+path['session_ids'].join('\",\"')+"\"]</div><div class='percent'>"+Math.round(path['count'] * 100 / totalCount)+"%</div><div class='numeric'>"+path['count'] +"/"+totalCount+"</div><div class='url'><a>"+path['url']+"</a></div><div class='clear'></div><div class='sub-paths'><img src='http://bzz.heroku.com/images/loading.gif' width='16' height='11'/> Loading...</div></div>";
	},
	pathResultsHtml: function(data, sessionOrder) {
		if (data['total_pageviews_in_query'] == 0) {
			return "<div class='end'>[end]</div>";
		}
		else {
			return $.map(data['results'], function(v,i) { return AdminPaths.pathHtml(v, data['total_pageviews_in_query'], sessionOrder); }).join('\n');
		}
	},
	bindPaths: function(paths) {
		paths.find('.url a').click(function(ev) {
			var path = $($(this).parents('.path')[0]);
			var subPaths = $(path.find('.sub-paths')[0]);
			if (path.hasClass('expanded')) {
				subPaths.slideDown(50);
				subPaths.slideUp(500, function() { path.removeClass('expanded'); path.addClass('collapsed'); });
			}
			else if (path.hasClass('subpath-loaded')) {
				subPaths.slideUp(50);
				subPaths.slideDown(500, function() { path.removeClass('collapsed'); path.addClass('expanded'); });
			}
			else {
				path.addClass('subpath-loaded');
				path.removeClass('collapsed');
				path.addClass('expanded');
				var url = path.find('.data-path-url').text();
				var nextOrder = parseInt(path.find('.data-path-order').text()) + 1;
				var sessionIds = path.find('.data-session-ids').text(); console.log(sessionIds);
				
				AdminPaths.fetchAndMergeData(nextOrder, 0, sessionIds, {total_pageviews_in_query:0, results: []}, function(data) {
					subPaths.slideUp(50);
					subPaths.html(AdminPaths.pathResultsHtml(data, nextOrder));
					subPaths.slideDown(500);
					AdminPaths.bindPaths(subPaths.find('.path'));
				});
			}
			
		});
	}
};
AdminPaths.init();