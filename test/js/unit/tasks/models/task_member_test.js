pavlov.specify("Task Member model unit tests", function() {

    describe("Task Member Model", function () {
        it("is a DS.Model", function() {
            assert(App.TaskMember).isDefined();
            assert(DS.Model.detect(App.TaskMember)).isTrue();
        });
    });
    
    describe("Task Member Instance", function () {

        before(function() {      
            Ember.run( function () {
                App.injectTestHelpers();
            });
        });

        after(function () {
            Ember.run( function () {
                App.removeTestHelpers();

                App.TaskMember.FIXTURES = [];
            });
        });

        it("should be a new task member");
        it("should have some properties");

    });

});