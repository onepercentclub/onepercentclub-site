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



App.UserMonthlyRoute = Em.Route.extend({});


App.UserMonthlyProfileRoute = Em.Route.extend({
    model: function(params) {
        var store = this.get('store');
        return App.RecurringDirectDebitPayment.find({status: 'recurring'}).then(function(recurringPayments) {
            if (recurringPayments.get('length') > 0) {
                return recurringPayments.objectAt(0);
            }else {
                return store.createRecord(App.RecurringDirectDebitPayment);
            }
        });
    }

});

App.UserMonthlyProjectsRoute = Em.Route.extend({
    model: function() {
        var route = this;
        return App.RecurringOrder.find({'status': 'recurring'}).then(function(recordList) {
            var store = route.get('store');
            if (recordList.get('length') > 0) {
                var record = recordList.objectAt(0);
                return record;
            } else {
                return store.createRecord(App.RecurringOrder);
            }
        })
    },
    setupController: function(controller, order) {
        this._super(controller, order);
        controller.startEditing();
        var store = this.get('store');

        // Set the top three projects
        App.ProjectPreview.find({ordering: 'popularity', phase: 'campaign'}).then(function(projects) {
            controller.set('topThreeProjects', projects.slice(0, 3));
        });

        // Set the recurring payment
        App.RecurringDirectDebitPayment.find({}).then(function(recurringPayments) {
            if (recurringPayments.get('length') > 0) {
                controller.set('payment', recurringPayments.objectAt(0));
            } else {
                controller.set('payment', store.createRecord(App.RecurringDirectDebitPayment));
            }
            var payment = controller.get('payment');
            payment.on('didError', function(record){
                payment.set('errors', record.get('errors'));
            });
        });
    },
    exit: function(){
        this.get('controller').stopEditing();
    }

});


App.UserMonthlyDonationListRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('userMonthlyProjects').get('donations');
    }
});

