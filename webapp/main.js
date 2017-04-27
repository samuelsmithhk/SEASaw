$("[data-media]").on("click", function(e) {
    e.preventDefault();
    var $this = $(this);
    var videoUrl = $this.attr("data-media");
    var popup = $this.attr("href");
    var $popupIframe = $(popup).find("iframe");

    $popupIframe.attr("src", videoUrl);
    $('html, body').animate({
      scrollTop: $popupIframe.offset().top
    }, 400);
    $this.closest(".results").addClass("show-popup");
});

$(".popup").on("click", function(e) {
    e.preventDefault();
    e.stopPropagation();
    $('#popframe').attr("src","about:blank")
    $(".results").removeClass("show-popup");
    
});

$(".popup > iframe").on("click", function(e) {
    e.stopPropagation();
});