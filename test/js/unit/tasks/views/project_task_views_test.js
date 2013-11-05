pavlov.specify('Project Task Edit View Tests', function() {

    describe('App.ProjectTaskEditView Class', function () {
        it('should be an Ember.View', function() {
            assert(App.ProjectTaskEditView).isDefined();
            assert(Ember.View.detect(App.ProjectTaskEditView)).isTrue();
        });
    });

    describe('App.ProjectTaskEditView Instance', function () {

        var view;

        before(function () {
            Ember.run( function () {
                view = App.ProjectTaskEditView.create();
            });
        });

        it('should respond to submit action', function() {
            assert(view.submit).isFunction();
        });

        it('should call updateTask when submit action triggered', function () {
            // stub some stuff
            var event = { preventDefault: function () {} };
            var controller = { updateTask: function () {} };
            var spy = sinon.spy(controller, 'updateTask');

            // call submit
            view.set('controller', controller);
            view.submit(event);

            assert(spy.calledOnce).isTrue();
        });
    });
 });

pavlov.specify('Project Task New View Tests', function() {

    describe('App.ProjectTaskNewView', function () {
        it('should be an Ember.View', function() {
            assert(App.ProjectTaskNewView).isDefined();
            assert(Ember.View.detect(App.ProjectTaskNewView)).isTrue();
        });
    });

    describe('App.ProjectTaskNewView Instance', function () {

        var view;

        before(function () {
            Ember.run( function () {
                view = App.ProjectTaskNewView.create();
            });
        });

        it('should respond to submit action', function() {
            assert(view.submit).isFunction();
        });

        it('should call newTask when submit action triggered', function () {
            // stub some stuff
            var event = { preventDefault: function () {} };
            var controller = { addTask: function () {} };
            var spy = sinon.spy(controller, 'addTask');

            // call submit
            view.set('controller', controller);
            view.submit(event);

            assert(spy.calledOnce).isTrue();
        });
    });
 });