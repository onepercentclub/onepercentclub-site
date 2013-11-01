pavlov.specify("Project model unit tests", function() {

    describe("Project Model", function () {
        it("is a DS.Model", function() {
            assert(App.Project).isDefined();
            assert(DS.Model.detect(App.Project)).isTrue();
        });
    });
    
    describe("Project Instance", function () {

        var project;

        before(function() {
            Ember.run(App, function() {
                App.advanceReadiness();
                loadProjectFixtures();

                project = App.Project.find('icswaterenterprisescambodia');
            });
        });

        after(function() {
            Ember.run(function() {
                App.reset();
            });
        });

        // FIXME:   The fixture data loaded in the before block either isn't being loaded
        //          or the Project find isn't working because the tests below are failing :-(

        // it("should have some properties", function () {
        //     assert(project.url).equals('projects/projects');
        //     assert(project.get('description')).equals('This project is an example of civic driven change.');
        //     assert(project.get("title")).equals('Two water enterprises Northern Cambodia');
        //     assert(project.get('plan')).equals();
        //     assert(project.get('campaign')).equals(null);
        //     assert(project.get('wallposts')).isDSArray();
        // });
    });

});