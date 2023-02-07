var $status = $('.quastion-count');
var $slickElement = $('.answers-tables');

$slickElement.on('init reInit afterChange', function (event, slick, currentSlide, nextSlide) {
    var i = (currentSlide ? currentSlide : 0) + 1;
    $status.text(i + '/' + slick.slideCount);
});

$slickElement.slick({
    arrows: true,
    speed: 500,
    // fade: true,
    infinite: false,
    cssEase: 'linear',
    nextArrow: '.next-question',
    prevArrow: '.previous-question',
    draggable: false,
    adaptiveHeight: true,
});