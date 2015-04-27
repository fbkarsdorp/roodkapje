var wrap = $("#wrapper");

wrap.on("scroll", function(e) {

  if (this.scrollTop > 147) {
    wrap.addClass("fix-story");
  } else {
    wrap.removeClass("fix-story");
  }

});