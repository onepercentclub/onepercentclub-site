/*
  Bluebottle Route Overrides
 */
App.ApplicationRoute.reopen({
    actions: {
        addDonation: function (project, fundraiser) {
            var route = this;
            App.CurrentOrder.find('current').then(function(order) {
                var store = route.get('store');

                var projectHasDonation = order.get('donations').anyBy('project', project);
                var fundraiserHasDonation = false;
                if(fundraiser !== undefined){
                    fundraiserHasDonation = order.get('donations').anyBy('fundraiser', fundraiser);
                }

                // TODO: functional test this.
                // *  Donate directly to project: check if no direct donations exist
                // *  Donate through fundraiser: check if donation for that fundraiser exists
                // *  We can have the same project multiple times, but all different fundraisers
                
                if (fundraiserHasDonation ||
                    (projectHasDonation && !fundraiserHasDonation && fundraiser === undefined)) {
                    // Donation for this already exists in this order.
                } else {
                    var donation = store.createRecord(App.CurrentOrderDonation);
                    donation.set('project', project);
                    if(fundraiser !== undefined){
                        donation.set('fundraiser', fundraiser);
                    }
                    donation.set('order', order);
                    donation.save();
                }
                route.transitionTo('currentOrder.donationList');
            });
        }
    }
});

/*
  Bluebottle Controller Overrides
 */
App.ApplicationController.reopen({
    needs: ['currentUser', 'currentOrder', 'myProjectList'],
});

/*
  Bluebottle View Overrides
 */
App.ApplicationView.reopen(App.Scrolling, {
	setBindScrolling: function() {
		this.bindScrolling();
	}.on('didInsertElement'),

	setUnbindScrolling: function() {
		this.unbindScrolling();
	}.on('didInsertElement'),

	scrolled: function(dist) {
		top = $('#content').offset();
		elm = top.screen.availTop;

		if (dist < elm) {
			$('#header').removeClass('is-scrolled');
			$('.nav-member-dropdown').removeClass('is-scrolled');
		} else {
			$('#header').addClass('is-scrolled');
			$('.nav-member-dropdown').addClass('is-scrolled');
		}
	}
});

/*
  Some 1%Club Mixins
 */
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