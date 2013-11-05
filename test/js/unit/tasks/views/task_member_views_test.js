pavlov.specify('Task Member Edit View Tests', function() {

    describe('App.TaskMemberEdit Class', function () {
        it('should be an Ember.View', function() {
            assert(App.TaskMemberEdit).isDefined();
            assert(Ember.View.detect(App.TaskMemberEdit)).isTrue();
        });
    });

    describe('App.TaskMemberEdit Instance', function () {

        var view;

        before(function () {
            Ember.run( function () {
                view = App.TaskMemberEdit.create();
            });
        });

        it('should respond to submit action', function() {
            assert(view.submit).isFunction();
        });

        it('should call updateTaskMember when submit action triggered', function () {
            // stub some stuff
            var event = { preventDefault: function () {} };
            var controller = { updateTaskMember: function () {} };
            var spy = sinon.spy(controller, 'updateTaskMember');

            // call submit
            view.set('controller', controller);
            view.submit(event);

            assert(spy.calledOnce).isTrue();
        });
    });
 });