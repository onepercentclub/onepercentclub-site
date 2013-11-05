pavlov.specify('Project Task List Route Tests', function() {

    describe('App.ProjectTaskListRoute Class', function () {
        it('should be an Ember.Route', function() {
            assert(App.ProjectTaskListRoute).isDefined();
            assert(Ember.Route.detect(App.ProjectTaskListRoute)).isTrue();
        });
    });

    describe('App.ProjectTaskListRoute Instance', function () {

        var route;

        before(function () {
            Ember.run( function () {
                route = App.ProjectTaskListRoute.create();
            });
        });

        it('should have an empty model property', function() {
        	var model = route.model();
            assert(model).isEmptyArray();
        });

        it('should add project tasks to controller when calling setupController');
    });
 });