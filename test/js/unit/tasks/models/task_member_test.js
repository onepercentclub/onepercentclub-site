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

        it("should be a new task search", function () {
            build('taskMember').then(function(taskMember) {
                assert(taskMember instanceof App.TaskMember).isTrue();
                assert(taskMember.get('isNew')).isTrue();
            });
        });

        it("should have some properties", function () {
            build('taskMember').then(function(taskMember) {
                assert(taskMember.url).equals('tasks/members');
                assert(taskMember.get('member') instanceof App.UserPreview).isTrue();
                assert(taskMember.get('task') instanceof App.Task).isTrue();
                assert(taskMember.get('motivation')).equals('Build a better Death Star');
                assert(taskMember.get('status')).equals('applied');
            });
        });

        it('should set status correctly', function () {
            build('taskMember').then(function(taskMember) {
                assert(taskMember.get('isStatusApplied')).isTrue('status should be applied');

                taskMember.set('status', 'accepted');
                return taskMember;
            }).then( function(taskMember) {
                assert(taskMember.get('isStatusAccepted')).isTrue('status should be accepted');

                taskMember.set('status', 'rejected');
                return taskMember;
            }).then( function(taskMember) {
                assert(taskMember.get('isStatusRejected')).isTrue('status should be rejected');

                taskMember.set('status', 'realized');
                return taskMember;
            }).then( function(taskMember) {
                assert(taskMember.get('isStatusRealized')).isTrue('status should be realized');
            });
        });

    });

});