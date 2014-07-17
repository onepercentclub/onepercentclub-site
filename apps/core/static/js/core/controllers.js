App.TrackerController = Em.Controller.extend({

   init: function(){
       this._super();
       if (MIXPANEL_KEY && mixpanel) {
           this.set('_tracker', mixpanel);
       }
   }.observes('window'),

   trackEvent: function(name, properties){

       if (Em.typeOf(name) == 'string' && Em.typeOf(properties) == 'object') {
           this.get('_tracker').track(name, properties);
       }
    },

    setUserDetails: function(){
        if (this.get('currentUser.isAuthenticated')) {
            var user = this.get('currentUser');
            this.get('_tracker').register({
                "email": user.get('email'),
                "name": user.get('full_name')
            });
        }
    }.observes('currentUser.isAuthenticated')

});
