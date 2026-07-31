(function ($) {
  "use strict";

  // Spinner
  var spinner = function () {
    setTimeout(function () {
      if ($("#spinner").length > 0) {
        $("#spinner").removeClass("show");
      }
    }, 1);
  };
  spinner();

  // Initiate the wowjs
  new WOW().init();

  // Sticky Navbar
  $(window).scroll(function () {
    if ($(this).scrollTop() > 300) {
      $(".sticky-top").addClass("shadow-sm").css("top", "0px");
    } else {
      $(".sticky-top").removeClass("shadow-sm").css("top", "-100px");
    }
  });

  // Back to top button
  $(window).scroll(function () {
    if ($(this).scrollTop() > 300) {
      $(".back-to-top").fadeIn("slow");
    } else {
      $(".back-to-top").fadeOut("slow");
    }
  });
  $(".back-to-top").click(function () {
    $("html, body").animate({ scrollTop: 0 }, 1500, "easeInOutExpo");
    return false;
  });

  // Facts counter
  $('[data-toggle="counter-up"]').counterUp({
    delay: 10,
    time: 2000,
  });

  // Header carousel
  $(".header-carousel").owlCarousel({
    autoplay: true,
    smartSpeed: 1500,
    loop: true,
    nav: false,
    dots: true,
    items: 1,
    dotsData: true,
  });

  // About & Feature side carousels — height matches text column
  function syncSplitCarouselHeight() {
    var isDesktop = $(window).width() >= 992;

    $(".split-content-row").each(function () {
      var $row = $(this);
      var $textCol = $row.find(".about-text, .feature-text").first();
      var $mediaCol = $row.find(".split-content-media-col").first();
      var $carousel = $mediaCol.find(".split-content-carousel").first();

      if (!$textCol.length || !$mediaCol.length || !$carousel.length) return;

      if (!isDesktop) {
        $mediaCol.css({ height: "", maxHeight: "" });
        $carousel.css({ height: "", maxHeight: "" });
        return;
      }

      var textHeight = $textCol.outerHeight();
      $mediaCol.css({ height: textHeight + "px", maxHeight: textHeight + "px" });
      $carousel.css({ height: textHeight + "px", maxHeight: textHeight + "px" });
    });
  }

  $(".split-content-carousel").owlCarousel({
    autoplay: true,
    smartSpeed: 1200,
    loop: true,
    nav: false,
    dots: true,
    items: 1,
    autoplayHoverPause: true,
    onInitialized: syncSplitCarouselHeight,
    onResized: syncSplitCarouselHeight,
  });

  $(".split-content-carousel img").on("load", syncSplitCarouselHeight);
  syncSplitCarouselHeight();
  $(window).on("load resize", syncSplitCarouselHeight);
  setTimeout(syncSplitCarouselHeight, 300);
  setTimeout(syncSplitCarouselHeight, 1000);

  // Testimonials carousel
  $(".testimonial-carousel").owlCarousel({
    autoplay: true,
    smartSpeed: 1000,
    center: true,
    dots: false,
    loop: true,
    nav: true,
    navText: [
      '<i class="bi bi-arrow-left"></i>',
      '<i class="bi bi-arrow-right"></i>',
    ],
    responsive: {
      0: {
        items: 1,
      },
      768: {
        items: 2,
      },
    },
  });

  // Portfolio isotope and filter
  var portfolioIsotope = $(".portfolio-container").isotope({
    itemSelector: ".portfolio-item",
    layoutMode: "fitRows",
  });
  $("#portfolio-flters li").on("click", function () {
    $("#portfolio-flters li").removeClass("active");
    $(this).addClass("active");

    portfolioIsotope.isotope({ filter: $(this).data("filter") });
  });
})(jQuery);
