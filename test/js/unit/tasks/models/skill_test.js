pavlov.specify("Project model unit tests", function() {

    describe("Project Model", function () {
        it("is a DS.Model", function() {
            assert(App.Project).isDefined();
            assert(DS.Model.detect(App.Project)).isTrue();
        });
    });
    
    describe("Project Instance", function () {

        before(function() {      
            Ember.run( function () {
                App.injectTestHelpers();
            });
        });

        after(function () {
            Ember.run( function () {
                App.removeTestHelpers();

                App.Project.FIXTURES = [];
            });
        });

        it("should be a new project", function () {
            build('project').then(function(project) {
                assert(project instanceof App.Project).isTrue();
                assert(project.get('isNew')).isTrue();
            });
        });

        it("should have some properties", function () {
            build('project').then(function(project) {
                assert(project.url).equals('projects/projects');
                assert(project.get('slug')).equals('empire-strikes-back');
                assert(project.get('title')).equals('Empire Strikes Back');
            });
        });

        it('should set getProject correctly', function () {
            build('project').then(function(project) {
                assert(project.get('getProject') instanceof App.Project).isTrue();
            });
        });

    });

});