/**
 * Router mapping
 */

App.Router.map(function() {

    this.resource('page', {path: '/pages/:page_id'});
    this.resource('contactMessage', {path: '/contact'});
});



/* Static Pages */

App.PageRoute = Em.Route.extend(App.ScrollToTop, {
    model: function(params) {
        var model = App.Page.find(params.page_id);
        var route = this;
        model.on('becameError', function() {
            route.transitionTo('error.notFound');
        });
        return model;
    }
});

/* Contact Page */

App.ContactMessageRoute = Em.Route.extend({
    model: function(params) {
        var store = this.get('store');
        return store.createRecord(App.ContactMessage);
    }
});

