/**
 * Router Map
 */


App.Router.map(function() {

    this.resource('myDonations', {path: '/donations'}, function(){
        this.resource('myDonationList', {path: '/history'});

        this.resource('monthlyDonation', {path: '/monthly'}, function() {
            this.resource('monthlyDonationProjects', {path: '/projects'});
        });
    });

});

/**
 * Routes
 */


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
    },
    setupController: function(controller, order) {
        this._super(controller, order);
        controller.startEditing();
        var store = this.get('store');

        // Set the top three projects
        App.ProjectPreview.find({ordering: 'popularity', status: 5}).then(function(projects) {
            controller.set('topThreeProjects', projects.slice(0, 3));
        });
    },
    exit: function(transition){
        this.get('controller').stopEditing();
    }

});

