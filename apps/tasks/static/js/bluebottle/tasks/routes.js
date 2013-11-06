App.Router.map(function(){
    this.resource('taskList', {path: '/tasks'});
});



// Tasks

App.ProjectTasksIndexRoute = Em.Route.extend({
    model: function(params) {
        return Em.A();
    },

    setupController: function(controller, model) {
        this._super(controller, model);
        var project = this.modelFor('project');
        var tasks = App.Task.find({project: project.get('id')});
        tasks.addObserver('isLoaded', function() {
            tasks.forEach(function(record) {
                if (record.get('isLoaded')) {
                    controller.get('content').pushObject(record);
                }
            });
        });
    }
});


App.ProjectTaskRoute = Em.Route.extend({
    model: function(params) {
        return App.Task.find(params.task_id);
    },
    setupController: function(controller, model) {
        this._super(controller, model);

        var wallPostController = this.controllerFor('taskWallPostList');
        wallPostController.set('model', model.get('wallposts'));
        wallPostController.set('items', Em.A());
        wallPostController.set('page', 0);
    },
    actions: {
        applyForTask: function(task) {
            var route = this;
            var store = route.get('store');
            var taskMember = store.createRecord(App.TaskMember);
            var view = App.TaskMemberApplyView.create();


            Bootstrap.ModalPane.popup({
                heading: gettext('Apply for task'),
                bodyViewClass: view,
                primary: gettext('Apply'),
                secondary: gettext('Cancel'),
                callback: function(opts, e) {
                    e.preventDefault();
                    if (opts.primary) {
                        taskMember.set('task', task);
                        taskMember.set('motivation', view.get('motivation'));
                        taskMember.set('created', new Date());
                        taskMember.save();
                    }
                }
            });
        },
        uploadFile: function(task) {
            var route = this;
            var controller = this.controllerFor('taskFileNew');
            var view = App.TaskFileNewView.create();
            view.set('controller', controller);
            var store = route.get('store');
            var file = store.createRecord(App.TaskFile);
            controller.set('model', file);
            file.set('task', task);

            Bootstrap.ModalPane.popup({
                classNames: ['modal', 'large'],
                headerViewClass: Ember.View.extend({
                    tagName: 'p',
                    classNames: ['modal-title'],
                    template: Ember.Handlebars.compile('{{view.parentView.heading}}')
                }),
                heading: task.get('title'),
                bodyViewClass: view,
                primary: 'Save',
                secondary: 'Cancel',
                callback: function(opts, e) {
                    e.preventDefault();
                    if (opts.primary) {
                        file.save();
                    }
                    if (opts.secondary) {
                        file.deleteRecord();
                    }
                }
            });
        },
        showMoreWallPosts: function() {
            var controller = this.get('controller');
            var wallPostController = this.controllerFor('taskWallPostList');
            wallPostController.set('canLoadMore', false);
            var page = wallPostController.incrementProperty('page');
            var task = controller.get('model');
            var wps = App.TaskWallPost.find({task: task.get('id'), page: page});
            wps.addObserver('isLoaded', function() {
                wps.forEach(function(record) {
                    if (record.get('isLoaded')) {
                        wallPostController.get('content').pushObject(record);
                    }
                });
                wallPostController.set('canLoadMore', true);
            });
        },
        editTaskMember: function(taskMember) {
            var route = this;
            var controller = this.controllerFor('taskMemberEdit');
            controller.set('model', taskMember);
            var view = App.TaskMemberEdit.create();
            view.set('controller', controller);

            Bootstrap.ModalPane.popup({
                headerViewClass: Ember.View.extend({
                    tagName: 'p',
                    classNames: ['modal-title'],
                    template: Ember.Handlebars.compile('{{view.parentView.heading}}')
                }),
                heading: taskMember.get('member.full_name'),
                bodyViewClass: view,
                primary: 'Save',
                secondary: 'Cancel',
                callback: function(opts, e) {
                    e.preventDefault();
                    if (opts.primary) {
                        taskMember.save();
                    }
                    if (opts.secondary) {
                        taskMember.rollback();
                    }
                }
            });
        },
        stopWorkingOnTask: function(task) {
            alert('Not implemented. Sorry!');
        }
    }
});


App.ProjectTaskNewRoute = Em.Route.extend({

    setupController: function(controller, model) {
        this._super(controller, model);
        var store = this.get('store');
        var model = store.createRecord(App.Task);
        controller.set('content', model);
    }
});


App.ProjectTaskEditRoute = Em.Route.extend({
    model: function(params) {
        return App.Task.find(params.task_id);
    }
});

