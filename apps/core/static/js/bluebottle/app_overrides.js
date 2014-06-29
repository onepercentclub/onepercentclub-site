/*
  Setup user details for exception handling
 */

App.then(function(app) {
    App.CurrentUser.find('current').then(function(user) {
        if (typeof Raven == 'object') {
            Raven.setUser({
                id: user.get('id_for_ember'),
                name: user.get('full_name'),
                email: user.get('email'),
            });
        }
    });

    // Override the BB project / status search list
    // TODO: we should just define the 'list' when initializing
    //       and then BB should use it when setting up the list
    App.ProjectPhase.find().then(function(data){
        var list = [
            {id: 5, name: gettext("Running campaigns")},
            {id: [7,8], name: gettext("Finished campaigns")}
        ];
        App.ProjectPhaseSelectView.reopen({
            content: list
        });
    });

    // Facebook API ID 
    if (FACEBOOK_AUTH_ID)
        App.set('appId', FACEBOOK_AUTH_ID);


    app.appLogin = function (fbResponse) {
        debugger
        var _this = this;
        return Ember.RSVP.Promise(function (resolve, reject) {
            var hash = {
              url: "/api/social-login/facebook/",
              dataType: "json",
              type: 'post',
              data: fbResponse
            };

            hash.success = function (response) {
                App.AuthJwt.processSuccessResponse(response).then(function (user) {
                    // If success
                    debugger
                    var currentUsercontroller = App.__container__.lookup('controller:CurrentUser');
                    currentUsercontroller.set('model', user);
                    $('[rel=close]').click();
                }, function (error) {
                    // If failed
                    console.log("fail");
                });
            };

            hash.error = function (response) {
                var error = JSON.parse(response.responseText);
                Ember.run(null, reject, error);
            };

            Ember.$.ajax(hash);
        });
    };
});

/*
  Bluebottle Route Overrides
 */

App.ApplicationRoute.reopen(App.LogoutJwtMixin, Ember.FacebookMixin, {
    init: function () {
        this._super();

        // Set the facebook appId
        // TODO: move this to the server side settings
        this.set('appId', '1438115069790112');
    },

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
    needs: ['currentOrder', 'myProjectList'],

    missingCurrentUser: function () {
        // FIXME: should call the clearJwtToken action here but it isn't being called.
        delete localStorage['jwtToken'];
        App.set('jwtToken', null);
    },
});

App.EventMixin = Em.Mixin.create({

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
  },

  bindMobileClick: function() {
    toggleMenu = function() {
      $('.mobile-nav-holder').toggleClass('is-active');
    };

    closeMenu = function(event) {
      $('.mobile-nav-holder').removeClass('is-active');
    };

    $('.mobile-nav-btn').bind('click', toggleMenu);
    $('#content').bind('hover', closeMenu);
  }
});

/*
  Bluebottle View Overrides
*/

App.ApplicationView.reopen(App.EventMixin, {
    setBindScrolling: function() {
        this.bindScrolling();
    }.on('didInsertElement'),

    setUnbindScrolling: function() {
        this.unbindScrolling();
    }.on('didInsertElement'),

    setBindClick: function() {
        this.bindMobileClick();
    }.on('didInsertElement'),

    scrolled: function(dist) {
        top = $('#content').offset();
        elm = top.screen.availTop;

        if (dist <= 53) {
            $('#header').removeClass('is-scrolled');
            $('.nav-member-dropdown').removeClass('is-scrolled');
            $('.mobile-nav-holder').removeClass('is-scrolled');
            $('#content').append('<div class="scrolled-area"></div>');
        } else {
            $('#header').addClass('is-scrolled');
            $('.nav-member-dropdown').addClass('is-scrolled');
            $('.mobile-nav-holder').addClass('is-scrolled');
        }
    }
});
