App.Router.map(function(){
    this.resource('myProject', {path: '/my/projects/:id'}, function() {
		this.route('goal');
    });
    this.resource('projectDonationList', {path: '/fundraisers/:fundraiser_id/donations'});
});

App.MyProjectGoalRoute = App.MyProjectSubRoute.extend({});


