App.Router.map(function(){
    this.resource('myProject', {path: '/my/projects/:id'}, function() {
        this.route('goal');
    });
    this.resource('projectDonationList', {path: '/fundraisers/:fundraiser_id/donations'});

    this.resource('myPartnerProject', {path: '/my/partnerproject/:id'});


});


App.MyProjectStartRoute.reopen({
    googleConversion:{
        label: 'HQPlCJL-6wsQ7o7O1gM'
    }
});

App.MyProjectListRoute.reopen(App.AuthenticatedRouteMixin, {});
App.MyProjectSubRoute.reopen(App.AuthenticatedRouteMixin, {});
App.MyProjectGoalRoute = App.MyProjectSubRoute.extend({});


App.MyPartnerProjectRoute = Em.Route.extend({
    // Create a Project with PartnerOrganization set.
    model: function(params) {
        var store = this.get('store');
        var partner = store.find('Partner', params.id);
        return App.MyProject.createRecord({partner: partner});
    },
    afterModel: function(model, transition){
        this.transitionTo('myProject', model)
    }
});

