App.HomeRoute = Em.Route.extend({
    model: function(params) {
        return App.HomePage.find(App.get('language'));
    },

    activate: function() {

        if (this.get('tracker')) {
            this.get('tracker').trackEvent("Homepage visit", {});
        }
    }
});
