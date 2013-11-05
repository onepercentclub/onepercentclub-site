pavlov.specify('Task Member Edit View Tests', function() {

    describe('App.TaskFileNewView Class', function () {
        it('should be an Ember.View', function() {
            assert(App.TaskFileNewView).isDefined();
            assert(Ember.View.detect(App.TaskFileNewView)).isTrue();
        });
    });

    describe('App.TaskFileNewView Instance', function () {

        var view;

        before(function () {
            Ember.run( function () {
                view = App.TaskFileNewView.create();
            });
        });

        it('should respond to addFile action', function() {
            assert(view.addFile).isFunction();
        });

        it('should call uploadTaskFile when addFile action triggered', function () {
            // stub some stuff
            var event = { preventDefault: function () {} };
            var controller = { uploadTaskFile: function () {} };
            var spy = sinon.spy(controller, 'uploadTaskFile');

            // call submit
            view.set('controller', controller);
            view.addFile(event);

            assert(spy.calledOnce).isTrue();
        });
    });
 });