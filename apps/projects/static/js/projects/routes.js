App.Router.map(function(){
    this.resource('myProject', {path: '/my/projects/:id'}, function() {
		this.route('goal');
    });
});

App.MyProjectGoalRoute = App.MyProjectSubRoute.extend({});

