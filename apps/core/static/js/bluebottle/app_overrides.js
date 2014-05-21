App.ApplicationController.reopen({
    needs: ['currentUser', 'currentOrder', 'myProjectList'],
});


App.Scrolling = Em.Mixin.create({

	bindScrolling: function(opts) {
		var onScroll, self = this;

		onScroll = function() {
			var scrollTop = $(this).scrollTop();
			return self.scrolled(scrollTop);
		};

		$(window).bind('scroll', onScroll);
		$(document).bind('touchmove', onScroll);
	},

	unbindScrolling: function () {
		$(window).unbind('scroll');
		$(document).unbind('touchmove');
	}
});

App.ApplicationView.reopen(App.Scrolling, {
	didInsertElement: function() {
		this.bindScrolling();
	},

	willRemoveElement: function() {
		this.unbindScrolling();
	},

	scrolled: function(dist) {
		top = $('#content').offset();
		elm = top.screen.availTop;

		if (dist < elm) {
			$('#header').removeClass('is-scrolled');
		} else {
			$('#header').addClass('is-scrolled');
		}
	}
});