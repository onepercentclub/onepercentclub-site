App.Router.map(function(){
    this.resource('myProject', {path: '/my/projects/:id'}, function() {
        this.route('goal');
    });
    this.resource('projectDonationList', {path: '/fundraisers/:fundraiser_id/donations'});
});


App.MyProjectStartRoute.reopen({
    googleConversion:{
        label: 'HQPlCJL-6wsQ7o7O1gM'
    }
});

App.MyProjectListRoute.reopen(App.AuthenticatedRouteMixin, {});
App.MyProjectSubRoute.reopen(App.AuthenticatedRouteMixin, {});
App.MyProjectGoalRoute = App.MyProjectSubRoute.extend({});
