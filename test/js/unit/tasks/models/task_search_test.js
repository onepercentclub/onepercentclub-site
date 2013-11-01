pavlov.specify("Task Search model unit tests", function() {

    describe("Task Search Model", function () {
        it("is a DS.Model", function() {
            assert(App.TaskSearch).isDefined();
            assert(DS.Model.detect(App.TaskSearch)).isTrue();
        });
    });
    
    describe("Task Search Instance", function () {

        before(function() {      
            Ember.run( function () {
                App.injectTestHelpers();
            });
        });

        after(function () {
            Ember.run( function () {
                App.removeTestHelpers();

                App.TaskSearch.FIXTURES = [];
            });
        });

        it("should be a new task search");
        it("should have some properties");

    });

});