jQuery(document).ready(function($) {var owl = $("#genre_bangla");owl.owlCarousel({items : 5,autoPlay: 2000,stopOnHover : true,pagination : false,itemsDesktop : [1400,6],itemsDesktopSmall : [1300,5],itemsTablet: [768,4],itemsTabletSmall: false,itemsMobile : [479,3],});$(".next_bangla").click(function(){owl.trigger('owl.prev');})
$(".prev_bangla").click(function(){owl.trigger('owl.next');})
});