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



App.UserDonationRoute = Em.Route.extend({
    model: function() {
        var route = this;
        return App.RecurringDirectDebitPayment.find({}).then(function(recordList) {
            var store = route.get('store');
            if (recordList.get('length') > 0) {
                var record = recordList.objectAt(0);
                return record;
            } else {
                record = store.createRecord(App.RecurringDirectDebitPayment);
                return record
            }
        })
    }

});


App.UserMonthlyProfileRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('userDonation');
    },
    exit: function(){
        this.get('controller').stopEditing();
    }



});

App.UserMonthlyProjectsRoute = Em.Route.extend({

    model: function() {
        var route = this;
        return App.RecurringOrder.find({'status': 'recurring'}).then(function(recordList) {
            var store = route.get('store');
            if (recordList.get('length') > 0) {
                return recordList.objectAt(0);
            } else {
                return store.createRecord(App.RecurringOrder);
            }
        });
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
        controller.set('payment', this.modelFor('userDonation'));

        // Set Address
        App.CurrentUser.find('current').then(function(user) {
            controller.set('address', App.UserSettings.find(user.get('id_for_ember')));
        });
    },
    exit: function(transition){
        this.get('controller').stopEditing();
    }

});


App.UserMonthlyDonationListRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('userMonthlyProjects').get('donations');
    }
});

