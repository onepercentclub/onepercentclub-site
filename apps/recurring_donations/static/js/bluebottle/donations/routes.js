/**
 * Router Map
 */


App.Router.map(function() {

    this.resource('userDonationHistory', {path: '/donations'});

    this.resource('monthlyDonation', {path: '/donations/monthly'}, function() {
        this.resource('monthlyDonationProjects', {path: '/projects'});
    });

});

/**
 * Routes
 */

App.UserDonationHistoryRoute = Em.Route.extend({
    model: function(params) {
        return App.Order.find({status: 'closed'});
    }
});


App.MonthlyDonationRoute = Em.Route.extend({
    model: function() {
        var route = this;
        return App.MonthlyDonation.find({}).then(function(recordList) {
            var store = route.get('store');
            if (recordList.get('length') > 0) {
                var record = recordList.objectAt(0);
                return record;
            } else {
                record = store.createRecord(App.MonthlyDonation);
                return record
            }
        })
    }

});

App.MonthlyDonationProjectsRoute = App.MonthlyDonationRoute.extend({

    setupController: function(controller, order) {
        this._super(controller, order);
        controller.startEditing();
        var store = this.get('store');

        // Set the top three projects
        App.ProjectPreview.find({ordering: 'popularity', status: 5}).then(function(projects) {
            controller.set('topThreeProjects', projects.slice(0, 3));
        });

        // Set the recurring payment
        controller.set('payment', this.modelFor('userDonation'));

        // Set Address
        App.CurrentUser.find('current').then(function(user) {
            controller.set('profile', App.UserSettings.find(user.get('id_for_ember')));
        });
    },
    exit: function(transition){
        this.get('controller').stopEditing();
    }

});


App.MonthlyDonationProjectsIndexRoute = App.MonthlyDonationRoute.extend({});


App.MonthlyDonationListRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('userMonthlyProjects').get('donations');
    }
});

