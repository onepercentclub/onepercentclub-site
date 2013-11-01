pavlov.specify("Task File model unit tests", function() {

    describe("Task File Model", function () {
        it("is a DS.Model", function() {
            assert(App.TaskFile).isDefined();
            assert(DS.Model.detect(App.TaskFile)).isTrue();
        });
    });
    
    describe("Task File Instance", function () {

        before(function() {      
            Ember.run( function () {
                App.injectTestHelpers();
            });
        });

        after(function () {
            Ember.run( function () {
                App.removeTestHelpers();

                App.TaskFile.FIXTURES = [];
            });
        });

        it("should be a new project");
        it("should have some properties");

    });

});