/**
 * Router mapping
 */

App.Router.map(function() {

    this.resource('page', {path: '/pages/:page_id'});
    this.resource('contactMessage', {path: '/contact'});
});



/* Static Pages */

App.PageRoute = Em.Route.extend({
    model: function(params) {
        var page =  App.Page.find(params.page_id);
        var route = this;
        page.on('becameError', function() {
            route.transitionTo('error.notFound');
        });
        return page;
    }
});

/* Contact Page */

App.ContactMessageRoute = Em.Route.extend({
    model: function(params) {
        var store = this.get('store');
        return store.createRecord(App.ContactMessage);
    },
    setupController: function(controller, model) {
        window.scrollTo(0, 0);
        this._super(controller, model);
        controller.startEditing();
    },

    exit: function() {
        if (this.get('controller')) {
            this.get('controller').stopEditing();
        }
    }
});

