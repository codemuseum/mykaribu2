ExpandCommentArea = $.klass({
  onfocus: function() { 
    if(!this.element.hasClass("DOMControl_autogrow"))
    {
      this.element.removeClass("DOMControl_placeholder");
      this.element.addClass("DOMControl_autogrow");
      this.element.val("");
      this.element.next().show();
      this.element.next().next().show();
    }
  },
  onblur: function() { 
    if(this.element.val() == ""){
      this.element.removeClass("DOMControl_autogrow");
      this.element.addClass("DOMControl_placeholder");
      this.element.val("Write a Comment...");
      this.element.next().hide();
      this.element.next().next().hide();
    }

  }
});
$('.add_comment_text').attach(ExpandCommentArea);


SearchAreaText = $.klass({
  onfocus: function() { 
    $(".searchText").hide();
  },
  onblur: function() { 
    if(this.element.val() == ""){
      $(".searchText").show();
    }
  }
});
$('.search_box').attach(SearchAreaText);

SearchAreaText2 = $.klass({
  onclick: function() { 
    $("#searchBox").focus();
  }
});
$('.searchText').attach(SearchAreaText2);



HoverRow = $.klass({
  onmouseenter: function() { 
    this.element.addClass('status_bar_hover');
  },
  onmouseleave: function() { 
    this.element.removeClass('status_bar_hover');   
  }
});
$('#hoverable_row td').attach(HoverRow);

HoverQuery = $.klass({
  onmouseenter: function() { 
    this.element.addClass('query_hover');
  },
  onmouseleave: function() { 
    this.element.removeClass('query_hover');   
  }
});
$('.streamReturn').attach(HoverQuery);


HoverX = $.klass({
  onmouseenter: function() { 
    this.element.addClass('hover_x');
  },
  onmouseleave: function() { 
    this.element.removeClass('hover_x');   
  }
});
$('.hoverable_x').attach(HoverX);


RecordResult = $.klass({
  onclick: function() { 
    recordResultUrl(this.element.attr("href"));
  }
});
$('a.gs-title').attach(RecordResult);
$('a.gs-image').attach(RecordResult);
