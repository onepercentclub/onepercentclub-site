pavlov.specify("Task model unit tests", function() {

    describe("Task Model", function () {
        it("is a DS.Model", function() {
            assert(App.Task).isDefined();
            assert(DS.Model.detect(App.Task)).isTrue();
        });
    });
    
    describe("Task Instance", function () {

        var task;

        before(function() {      
            Ember.run( function () {
                App.injectTestHelpers();
            });

            build('task').then(function(record) {
                task = record;
            });
        });

        after(function () {
            Ember.run( function () {
                App.removeTestHelpers();

                App.Task.FIXTURES = [];
            });
        });

        it("should be a new task", function () {
            assert(task instanceof App.Task).isTrue();
            assert(task.get('isNew')).isTrue();
        });

        it("should have some properties", function () {
            build('task').then(function(task) {
                assert(task.url).equals('tasks');
                assert(task.get('description')).equals('Title says it all');
                assert(task.get('title')).equals('Takeover Naboo');
            });
        });

        it('should set status correctly', function () {
            build('task').then(function(task) {
                assert(task.get('isStatusOpen')).isTrue();

                task.set('status', 'in progress');
                return task;
            }).then( function(task) {
                assert(task.get('isStatusInProgress')).isTrue();

                task.set('status', 'closed');
                return task;
            }).then( function(task) {
                assert(task.get('isStatusClosed')).isTrue();

                task.set('status', 'realized');
                return task;
            }).then( function(task) {
                assert(task.get('isStatusRealized')).isTrue();
            });
        });

    });

});