App.Router.map(function(){
    this.resource('myProject', {path: '/my/projects/:id'}, function() {
        this.route('goal');
    });
    this.resource('projectDonationList', {path: '/fundraisers/:fundraiser_id/donations'});
});

App.MyProjectListRoute.reopen(App.AuthenticatedRouteMixin, {});
App.MyProjectSubRoute.reopen(App.AuthenticatedRouteMixin, {});
App.MyProjectGoalRoute = App.MyProjectSubRoute.extend({});
