$(document).ready(function(){
	initMore();
	initProfileViewer();
	initProgressBar();
});


function initMore(){
	$('.more').each(function(){
		if ($(this).parent().parent().find('.long').html().length 
				== $(this).parent().parent().find('.short').html().length) {
			$(this).hide();
		}
	});
	$('.more').click(function(){
		$(this).parent().parent().find('.long').show();
		$(this).parent().parent().find('.short').hide();
		return false;
	});
	$('.less').click(function(){
		$(this).parent().parent()('p').children('.long').hide();
		$(this).parent().parent()('p').children('.short').show();
		return false;
	});
	
}


function initProfileViewer(){
	$('.panelink').click(function(){
		var name = $(this).attr('for');
		$(this).parent().find('.pane').hide();
		$(this).parent().find('.' + name).show();
		return false;
	});
}


function initProgressBar(){
	$('.donated').each(function(){
		var width = $(this).css('width');
		$(this).css('width', 0);
		$(this).parents('.progressbar').find('.amount-donated').css({opacity: 0});
		$(this).animate({width: width}, 2000,function(){
			$(this).parents('.progressbar').find('.amount-donated').css({opacity: 1});
		});
		 
	});
}

