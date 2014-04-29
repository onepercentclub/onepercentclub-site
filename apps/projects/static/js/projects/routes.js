App.Router.map(function(){
    this.resource('myProject', {path: '/my/projects/:id'}, function() {
		this.route('goal');
    });
});

App.MyProjectGoalRoute = App.MyProjectSubRoute.extend({});

App.ProjectRoute.reopen({
    renderTemplate: function() {
        this._super();

        var controller = this.controllerFor('ProjectFundRaiserList');
        this.render('ProjectFundRaiserList', {
            into: 'project',
            outlet: 'fundraisers',
            controller: controller
        });
    }
})