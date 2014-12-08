/*
  Setup user details for exception handling
 */

App.then(function(app) {
    App.CurrentUser.find('current').then(function(user) {
        if (typeof Raven == 'object') {
            Raven.setUser({
                id: user.get('id_for_ember'),
                name: user.get('full_name'),
                email: user.get('email')
            });
        }
    });

    // This is called from the router automatically if the route being loaded
    // has a googleConversion property, otherwise it can be called manually. 
    // Pass Google conversion code - 'gc'
    app.trackConversion = function (gc) {
        Ember.run.next(function() {
            if (gc &! DEBUG) {
                var google_conversion_id = gc.id || 986941294;
                var google_conversion_language = gc.language || 'en';
                var google_conversion_format = gc.format || '3';
                var google_conversion_color = gc.color || 'ffffff';
                var google_conversion_label = gc.label;
                var google_remarketing_only = false;
                $.getScript("https://www.googleadservices.com/pagead/conversion.js");
            }
        });
    };

    // Override the BB project / status search list
    // TODO: we should just define the 'list' when initializing
    //       and then BB should use it when setting up the list
    App.ProjectPhase.find().then(function(data){
        var list = [
            {id: 5, name: gettext("Running Campaigns")},
            {id: [7,8], name: gettext("Finished Campaigns")}
        ];
        App.ProjectPhaseSelectView.reopen({
            content: list
        });
    });

    // Facebook API ID 
    if (FACEBOOK_AUTH_ID)
        App.set('appId', FACEBOOK_AUTH_ID);


    app.fbLogin = function (fbResponse) {
        
        var _this = this,
            currentUsercontroller = App.__container__.lookup('controller:currentUser');

        // Clear any existing tokens which might be present but expired. clearJwtToken action is on the App.ApplicationRoute
        // FIXME: should call the clearJwtToken action here but it isn't being called.
        // currentUsercontroller.send('clearJwtToken');
        delete localStorage.jwtToken;
        App.set('jwtToken', null);
            
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
                    currentUsercontroller.set('model', user);

                    // For some reason the currentUserController keeps failing to have a reference to 'tracker'
                    var loginController = App.__container__.lookup('controller:login'),
                        tracker = loginController.get('tracker');

                    if (tracker) {
                        if (user.get('firstLogin')) {
                            tracker.alias(user.get('id_for_ember'));
                        } else {
                            tracker.identify(user.get('id_for_ember'));
                        }

                        tracker.peopleSet({
                            "$first_name": user.get('first_name'),
                            "$last_name": user.get('last_name'),
                            "$email": user.get('email'),
                            has_facebook: "yes",
                            last_login_type: "facebook"
                        });

                    }

                    if (user.get('firstLogin')) {
                        currentUsercontroller.send('setFlash', currentUsercontroller.get('welcomeMessage'));
                        // Register the successful Facebook signup with Mixpanel
                        if (tracker) {
                            tracker.trackEvent("Signup", {"type": "facebook"});
                            tracker.peopleSet({
                                facebook_shares: 0,
                                twitter_shares: 0
                            });
                        }
                    } else {
                        // Register the successful Facebook signin with Mixpanel
                        if (tracker) {
                            tracker.trackEvent("Login", {"type": "facebook"});
                            tracker.peopleSet({has_facebook: "yes"});
                        }
                    }


                    Ember.run(null, resolve, user);
                    
                    // Trigger next transition in case a user was accesing a restricted page
                    currentUsercontroller.send('loadNextTransition'); 

                    if (FBApp.get('callingController')._handleSignupSuccess) {
                        FBApp.get('callingController')._handleSignupSuccess();
                    } else if (FBApp.get('callingController')._handleLoginSuccess) {
                        FBApp.get('callingController')._handleLoginSuccess();
                    } else {
                        currentUsercontroller.send('close');
                    }

                 }, function (error) {
                    // If Facebook login succeeded but something goes wrong on the token side we end up here
                    currentUsercontroller.send('setFlash', error, 'error');
                    Ember.run(null, reject, error);
                });
            };

            hash.error = function (response) {

                currentUsercontroller.send('setFlash', gettext('There was an error connecting Facebook'), 'error');
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

App.ApplicationRoute.reopen(App.LogoutJwtMixin, {
    actions: {
        logout: function (redirect) {
            // call the standard logout code => clear JWT token etc
            this._super(redirect);

            // If the has logged in via FB, eg there is a FBUser then they should 
            // be logged out so that the user can log in with user/email
            if (typeof FB == 'object' && !Em.isEmpty(FB.getUserID()))
                FB.logout();
        },
    }
});

/*
  Bluebottle Controller Overrides
 */
App.ApplicationController.reopen({
    needs: ['myProjectList'],
    missingCurrentUser: function () {
        // FIXME: should call the clearJwtToken action here but it isn't being called.
        delete localStorage.jwtToken;
        App.set('jwtToken', null);
    }
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

  startStopScrolling: function(elm, nameClass) {
    var lastScroll = 0,
        st, startScroll;

    startScroll = function() {
        st = $(this).scrollTop();

        if (st > lastScroll) {
            $(elm).removeClass(nameClass);
        } else {
            $(elm).addClass(nameClass);
        }

        lastScroll = st;
    };

    $(window).bind('scroll', startScroll);
    $(document).bind('touchmove', startScroll);
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

Ember.View.reopen({
    touchStart: Ember.computed.alias('click')
})

/*
  Bluebottle View Overrides
*/

App.ApplicationView.reopen(App.EventMixin, {
    setBindScrolling: function() {
        this.bindScrolling();
        this.startStopScrolling('#cheetah-header', 'is-active');
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
            //$('#content').append('<div class="scrolled-area"></div>');
        } else {
            $('#header').addClass('is-scrolled');
            $('.nav-member-dropdown').addClass('is-scrolled');
            $('.mobile-nav-holder').addClass('is-scrolled');
        }
    }
});


// Enable Google Ad Words with Ember
App.Router.reopen({

    // If you want to add Google conversion codes to a route just add:
    // googleConversion: {
    //      label: 'my_page_label'
    // }

    didTransition: function(infos) {
        this._super(infos);

        var currentRoute = infos.get('lastObject').handler,
            gc = currentRoute.get('googleConversion');

        if (gc) App.trackConversion(gc);
    },
});

// Order login controller needs the jwt mixin
App.OrderLoginController.reopen(App.AuthJwtMixin, {});
