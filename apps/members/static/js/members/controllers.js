App.LoginController.reopen({
    needs: ['currentUser'],

    loginTitle: 'Log in to 1% Club',
    actions: {
        login: function () {
            var _this = this;
            this.authorizeUser(this.get('username'), this.get('password')).then(function (user) {
                _this.set('controllers.currentUser.model', user);
                _this.send('closeAllModals');
            }, function (error) {
                // Do something here!
            });
        },
    },
    authorizeUser: function (username, password) {
        var _this = this,
            username = _this.get('username'),
            password = _this.get('password');
        
        return Ember.RSVP.Promise(function (resolve, reject) {
            var hash = {
              url: "/api-token-auth/",
              dataType: "json",
              type: 'post',
              data: {
                  username: username,
                  password: password
              }
            };
           
            hash.success = function (response) {
              // User authentication succeeded. Store the token:
              App.set('jwtToken', response.token);

              // In Ember Data < beta the App.CurrentUser gets stuck in the root.error
              // state so we need to force a transition here before trying to fetch the
              // user again.
              currentUser = App.CurrentUser.find('current');
              if (currentUser.get('currentState.error.stateName') == 'root.error') {
                  currentUser.transitionTo('deleted.saved')
                  currentUser = App.CurrentUser.find('current').then( function (user) {
                      Ember.run(null, resolve, user);
                  });
              } else {
                  Ember.run(null, resolve, currentUser);
              }
            };
           
            hash.error = function (response) {
                debugger
                Ember.run(null, reject, error);
            };
           
            Ember.$.ajax(hash);
        });
    }
});