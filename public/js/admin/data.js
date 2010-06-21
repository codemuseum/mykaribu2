var AdminData = {
  sourceUrl: $('#data-source')[0].href,
  dataTable: $('#data'),
  properties: $('#data th.property'),
  init: function() {
      this.fetchDataLoop(null, function() {
        if (document.location.hash.substring(1) != '') {
          $('#'+document.location.hash.substring(1)).addClass('hilighted');
        }
      });
  },
  fetchDataLoop: function(cursor, callback) {
    var cursorParam = cursor == null ? {} : {'cursor': cursor};
    $.post(this.sourceUrl, cursorParam, function(data) {
			if (data['count'] == 0) { $('#loading-msg').fadeOut(); callback(); }
	        else {
                for (var i in data['results']) { AdminData.appendDataRow(data['results'][i]); }
				AdminData.fetchDataLoop(data['cursor'], callback);
			}
	}, 'json');
  },
  appendDataRow: function(row) {
    var propertiesHtml = '';
    this.properties.each(function(i,v) {  propertiesHtml += '<td class="property">'+row[$(v).text()]+'</td>'; });
    
    this.dataTable.append('<tr id="key_'+row['__key__']+'">' + propertiesHtml+ '</tr>');
  }
};
AdminData.init();