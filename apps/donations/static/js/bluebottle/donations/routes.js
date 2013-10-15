/**
 * Router Map
 */


App.Router.map(function() {

    this.resource('userDonation', {path: '/donations'}, function() {
        this.resource('userDonationHistory', {path: '/'});
        this.resource('userMonthlyProjects', {path: '/projects'});
        this.resource('userMonthlyProfile', {path: '/profile'});
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



App.UserMonthlyRoute = Em.Route.extend({
    model: function() {
        var route = this;
        return App.RecurringDirectDebitPayment.find({}).then(function(recordList) {
                var store = route.get('store');
                if (recordList.get('length') > 0) {
                    var record = recordList.objectAt(0);
                    return record;
                } else {
                    return store.createRecord(App.RecurringDirectDebitPayment);
                }
            }
        )
    },
    setupController: function(controller, donations) {
        this._super(controller, donations);
        // Set the monthly order.
        App.Order.find({status: 'recurring'}).then(function(recurringOrders) {
            if (recurringOrders.get('length') > 0) {
                controller.set('order', recurringOrders.objectAt(0))
            } else {
                controller.set('order', null)
            }
        });

        // Set the top three projects
        App.ProjectPreview.find({ordering: 'popularity', phase: 'campaign'}).then(function(projects) {
            controller.set('topThreeProjects', projects.slice(0, 3));
        });

        // set the recurring payment
        App.RecurringDirectDebitPayment.find({}).then(function(recurringPayments) {
            if (recurringPayments.get('length') > 0) {
                controller.set('recurringPayment', recurringPayments.objectAt(0));
            }else {
                controller.set('recurringPayment', null);
            }
        });
    }

});


App.UserMonthlyProfileRoute = App.UserMonthlyRoute.extend({});

App.UserMonthlyProjectsRoute = App.UserMonthlyRoute.extend({});


App.UserMonthlyDonationListRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('userMonthly').get('order.donations');
    },

    setupController: function(controller, donations) {
        this._super(controller, donations);

        console.log(controller);
        console.log(donations);
    }
});

