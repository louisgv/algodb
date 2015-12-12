$(function() {
  // Toggle logo color
  $('.logo').click(function() {
    if ($('.logo .v1').hasClass('hidden')) {
      $('.logo .v1').removeClass('hidden');
      $('.logo .v2').addClass('hidden');
    } else {
      $('.logo .v2').removeClass('hidden');
      $('.logo .v1').addClass('hidden');
    }
  });

  // Toggle see more expand/collapse
  $('.see-more-button').click(function() {
    var $result = $(this).closest('.result');
    var $seeMore = $result.find('.see-more');
    if ($seeMore.hasClass('hidden')) {
      $result.find('.see-more-button').text('Hide more');
    } else {
      // Hide content
      $result.find('.see-more-button').text('See more');
      if (!$(this).hasClass('top')) {
        $('body').scrollTop($result.offset().top);
      }
    }
    $seeMore.toggleClass('hidden');
  });

  // Expand/collapse all
  $('.expand-hide').click(function() {
    if ($(this).hasClass('expanded-all')) {
      // hide all
      $('.see-more').addClass('hidden');
      $('.see-more-button').text('See more');
    } else {
      // expand/show all
      $('.see-more').removeClass('hidden');
      $('.see-more-button').text('Hide more');
    }
    $(this).toggleClass('expanded-all');
  });
});