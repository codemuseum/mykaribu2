var AdminData = {
  sourceUrl: $('#data-source')[0].href,
  dataTable: $('#data'),
  properties: $('#data th.property'),
  init: function() {
    this.fetchDataLoop(0, function() {
      console.log("done");
    });
  },
  fetchDataLoop: function(page, callback) {
    $.getJSON(this.sourceUrl, {'page': page}, function(data) {
			if (data['count'] == 0) { $('#loading-msg').fadeOut(); callback(); }
			else {
        for (var i in data['results']) { AdminData.appendDataRow(data['results'][i]); }
				AdminData.fetchDataLoop(page + 1, callback);
			}
		});
  },
  appendDataRow: function(row) {
    var propertiesHtml = '';
    this.properties.each(function(i,v) {  propertiesHtml += '<td class="property">'+row[$(v).text()]+'</td>'; });
    
    this.dataTable.append('<tr id="key_'+row['__key__']+'">' + propertiesHtml+ '<td><a name="key_'+row['__key__']+'"></a></td></tr>');
  }
};
AdminData.init();