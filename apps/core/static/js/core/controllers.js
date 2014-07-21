App.TrackerController = Em.ObjectController.extend({
   needs: "currentUser",

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
        if (this.get('controllers.currentUser.isAuthenticated')) {
            var user = this.get('controllers.currentUser');
            this.get('_tracker').register({
                "email": user.get('email'),
                "name": user.get('full_name')
            });
        }
    }.observes('controllers.currentUser.isAuthenticated')

});
