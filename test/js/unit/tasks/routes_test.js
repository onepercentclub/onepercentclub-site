pavlov.specify('Project Tasks Route Tests', function() {

    describe('App.ProjectTasksIndexRoute Class', function () {
        it('should be an Ember.Route', function() {
            assert(App.ProjectTasksIndexRoute).isDefined();
            assert(Ember.Route.detect(App.ProjectTasksIndexRoute)).isTrue();
        });
    });

    describe('App.ProjectTasksIndexRoute Instance', function () {

        var route;

        before(function () {
            Ember.run( function () {
                route = App.ProjectTasksIndexRoute.create();
            });
        });

        it('should have an empty model property', function() {
        	var model = route.model();
            assert(model).isEmptyArray();
        });

        it('should add project tasks to controller when calling setupController', function () {
            expect(0); // Expect 0 Assertions == Not Implemented
        });
    });
    
 });