App.HomeRoute = Em.Route.extend({
    model: function(params) {
        return App.HomePage.find(App.get('language'));
    },

    setupController: function(controller, model) {
        this._super(controller, model);
    }
});
