/*
 Controllers
 */


// This is the controller to show the wallposts
App.ProjectIndexController = Em.ArrayController.extend(App.ShowMoreItemsMixin, {});


App.ProjectWallPostNewController = Em.ObjectController.extend({
    needs: ['currentUser', 'projectIndex', 'project'],

    // This a temporary container for App.Photo records until they are connected after this wallpost is saved.
    files: Em.A(),

    init: function() {
        this._super();
        this.set('content', App.NewProjectWallPost.createRecord());
    },

    addMediaWallPost: function() {
        var store = this.get('store');
        var mediawallpost = store.createRecord(App.ProjectMediaWallPost);
        var controller = this;
        mediawallpost.set('title', this.get('content.title'));
        mediawallpost.set('text', this.get('content.text'));
        mediawallpost.set('video_url', this.get('content.video_url'));
        mediawallpost.set('project', this.get('controllers.project.model'));



        mediawallpost.on('didCreate', function(record) {
            Ember.run.next(function() {
                if (controller.get('files').length) {
                    // Connect all photos to this wallpost.
                    var reload = true;
                    controller.get('files').forEach(function(photo){
                        photo.set('mediawallpost', record);
                        photo.save();
                    });
                    // Empty this.files so we can use it again.
                    controller.set('files', Em.A());
                }
                var list = controller.get('controllers.projectIndex.items');
                list.unshiftObject(record);
                controller.clearWallPost()
            });
        });
        mediawallpost.on('becameInvalid', function(record) {
            controller.set('errors', record.get('errors'));
//            TODO: The record needs need to be deleted somehow.
//            record.deleteRecord();
        });
        mediawallpost.save();
    },

    addFile: function(file) {
        var transaction = this.get('store').transaction();
        var photo = transaction.createRecord(App.ProjectWallPostPhoto);
        // Connect the file to it. DRF2 Adapter will sort this out.
        photo.set('photo', file);
        transaction.commit();
        var controller = this;
        // Store the photo in this.files. We need to connect it to the wallpost later.
        photo.on('didCreate', function(record){
            controller.get('files').pushObject(photo);
        });
    },

    removePhoto: function(photo) {
        var transaction = this.get('store').transaction();
        transaction.add(photo);
        photo.deleteRecord();
        transaction.commit();
        // Remove it from temporary array too.
        this.get('files').removeObject(photo);
    },

    addTextWallPost: function() {
        var transaction = this.get('store').transaction();
        var textwallpost = transaction.createRecord(App.ProjectTextWallPost);
        textwallpost.set('text', this.get('content.text'));
        textwallpost.set('project', this.get('controllers.project.model'));
        var controller = this;
        textwallpost.on('didCreate', function(record) {
            // This is an odd way of getting to the parent controller
            var list = controller.get('controllers.projectIndex.items');
            list.unshiftObject(record);
            controller.clearWallPost()
        });
        textwallpost.on('becameInvalid', function(record) {
            controller.set('errors', record.get('errors'));
//            TODO: The record needs need to be deleted somehow.
//            record.deleteRecord();
        });
        transaction.commit();
    },

    clearWallPost: function() {
        this.set('content.title', '');
        this.set('content.text', '');
        this.set('content.video_url', '');
        this.set('content.errors', null);
    },

    isProjectOwner: function() {
        var username = this.get('controllers.currentUser.username');
        var ownername = this.get('controllers.project.model.owner.username');
        if (username) {
            return (username == ownername);
        }
        return false;
    }.property('controllers.project.model.owner', 'controllers.currentUser.username')

});


App.WallPostController = Em.ObjectController.extend(App.IsAuthorMixin, {
    needs: ['currentUser'],

    newReaction: function(){
        var transaction = this.get('store').transaction();
        return transaction.createRecord(App.WallPostReaction, {'wallpost': this.get('model')});
    }.property('model'),

    actions: {
        deleteRecordOnServer: function(){
            var model = this.get('model');
            model.deleteRecord();
            model.save();
        }
    }
});

App.TaskWallPostListController = Em.ArrayController.extend(App.ShowMoreItemsMixin, {
    needs: ['currentUser']
});


App.TaskWallPostNewController = Em.ObjectController.extend({
    needs: ['currentUser', 'taskWallPostList', 'projectTask'],
    init: function() {
        this._super();
        var store = this.get('store');
        var wallPost = store.createRecord(App.TaskWallPost);
        this.set('content', wallPost);
    },
    addTextWallPost: function() {
        var controller = this;
        var wallpost = this.get('content');
        // Parent-parent controller is the task

        var task = this.get('controllers.projectTask.model');

        wallpost.set('task', task);
        wallpost.on('didCreate', function(record) {
            var taskList = controller.get('controllers.taskWallPostList.items');
            taskList.unshiftObject(record);
            // Init again to set up a new model for the form.
            controller.init();
        });
        wallpost.on('becameInvalid', function(record) {
            controller.set('errors', record.get('errors'));
//            TODO: The record needs need to be deleted somehow.
//            record.deleteRecord();
        });
        wallpost.save();
    }

});


/* Reactions */

App.WallPostReactionController = Em.ObjectController.extend(App.IsAuthorMixin, App.DeleteModelMixin, {
    needs: ['currentUser']
});


App.WallPostReactionListController = Em.ArrayController.extend({
    needs: ['currentUser'],

    init: function() {
        this._super();
        this.createNewReaction();
    },

    createNewReaction: function() {
        var store = this.get('store');
        var reaction =  store.createRecord(App.WallPostReaction);
        this.set('newReaction', reaction);
    },

    addReaction: function() {
        var reaction = this.get('newReaction');
        // Set the wallpost that this reaction is related to.
        reaction.set('wallpost', this.get('target.model'));
        reaction.set('created', new Date());
        var controller = this;
        reaction.on('didCreate', function(record) {
            controller.createNewReaction();
            // remove is-selected from all input roms
            $('form.is-selected').removeClass('is-selected');
        });
        reaction.on('becameInvalid', function(record) {
            controller.createNewReaction();
            controller.set('errors', record.get('errors'));
            record.deleteRecord();
        });
        reaction.save();
    }
});
