pavlov.specify("Task model unit tests", function() {

    describe("Task Model", function () {
        it("is a DS.Model", function() {
            assert(App.Task).isDefined();
            assert(DS.Model.detect(App.Task)).isTrue();
        });
    });
    
    describe("Task Instance", function () {

        before(function() {      
            Ember.run( function () {
                App.injectTestHelpers();
            });
        });

        after(function () {
            Ember.run( function () {
                App.removeTestHelpers();

                App.Task.FIXTURES = [];
            });
        });

        it("should be a new task", function () {
            build('task').then(function(task) {
                assert(task instanceof App.Task).isTrue();
                assert(task.get('isNew')).isTrue();
            });
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
                assert(task.get('isStatusOpen')).isTrue('status should be open');

                task.set('status', 'in progress');
                return task;
            }).then( function(task) {
                assert(task.get('isStatusInProgress')).isTrue('status should be in progress');

                task.set('status', 'closed');
                return task;
            }).then( function(task) {
                assert(task.get('isStatusClosed')).isTrue('status should be closed');

                task.set('status', 'realized');
                return task;
            }).then( function(task) {
                assert(task.get('isStatusRealized')).isTrue('status should be realized');
            });
        });

        describe('#timeNeeded', function () {

            it('should return friendly time for specific times', function () {
                build('task', {time_needed: 8}).then(function(task) {
                    assert(task.get('timeNeeded')).equals('one day', 'time needed from App.TimeNeededList');
                });
            });

            it('should return time in hours for non-specific times', function () {
                build('task', {time_needed: 2}).then(function(task) {
                    assert(task.get('timeNeeded')).equals('two hours', 'time needed in hours');
                });
            });

        });

    });

});