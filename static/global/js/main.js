$(document).ready(function() {
	init();
});
function init(container) {
	initMore(container);
	initProfileViewer(container);
	initProgressBar(container);
	initAjax(container);
}

function initAjax(container) {
	$('a.ajax', container).unbind('click');
	$('a.ajax', container).click(function() {
		var url = $(this).attr('href');
		BlueApp.routers.Main.navigate(url, {
			trigger : true
		});
		return false;
	});

	$('form.ajax', container).submit(function() {
		var url = $(this).attr('action') + "/?" + $(this).serialize();
		BlueApp.routers.Main.navigate(url, {
			trigger : true
		});
		return false;

	});
}

function initMore() {
	$('.more').each(function() {
		if($(this).parent().parent().find('.long').html().length == $(this).parent().parent().find('.short').html().length) {
			$(this).hide();
		}
	});
	$('.more').unbind('click');
	$('.more').click(function() {
		$(this).parent().parent().find('.long').show();
		$(this).parent().parent().find('.short').hide();
		return false;
	});
	$('.less').unbind('click');
	$('.less').click(function() {
		$(this).parent().parent().find('.long').hide();
		$(this).parent().parent().find('.short').show();
		return false;
	});
}

function initProfileViewer() {
	$('.panelink').unbind('mouseover');
	$('.panelink').mouseover(function() {
		var name = $(this).attr('for');
		$(this).parent().find('.pane').hide();
		$(this).parent().find('.' + name).show();
		return false;
	});
}

function initProgressBar() {
	$('.progressbar').each(function() {
		var pb = $(this);
		var donated = pb.find('.donated-amount').html();
		var asked = pb.find('.asked-amount').html();
		var donText = pb.find('.donated-text');
		var donBar = pb.find('.donated-bar');
		var pct = 0;
		if(asked) {
			pct = 100 * donated / asked;
			pct = Math.round(pct);
		}
		donText.css({
			opacity : 0
		});
		donBar.css({
			width : 0
		});
		donBar.animate({
			width : pct + '%'
		}, 2000, function() {
			donText.css({
				opacity : 1
			});
		});
		if(pct < 40) {
			pct = pct + '%';
			donText.addClass('left');
			donText.css({
				'margin-left' : pct
			});

		} else {
			pct = 100 - pct + '%';
			donText.addClass('right');
			donText.css({
				'margin-right' : pct
			});
		}

	});
}