
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


App.TextWallPostNewController = Em.ObjectController.extend({
    /**
     * This is the base class for a wall-post form.
     *
     * To use it extend it and add:
     * - Extend 'needs' to have parent object and wall-post list controllers.
     * - Overwrite 'parentId' to return the id of the parent object.
     * - Overwrite 'wallPostList' to return the array (model) that holds the wall-post list.
     * - Define a 'type'
     *
     * Look at App.ProjectTextWallPostNewController for example
     */

    needs: ['currentUser'],

    parentId: function(){
        return Em.K();
    }.property(),

    wallPostList: function(){
        return Em.K();
    }.property(),

    type: Em.K(),

    init: function() {
        this._super();
        this.createNewWallPost();
    },
    actions: {
        saveWallPost: function() {
            var wallPost = this.get('model');
            wallPost.set('parent_id', this.get('parentId'));
            wallPost.set('parent_type', this.get('type'));
            wallPost.set('type', 'text');

            var controller = this;
            wallPost.on('didCreate', function(record) {
                var list = controller.get('wallPostList');
                list.unshiftObject(record);
                controller.createNewWallPost()
            });
            wallPost.on('becameInvalid', function(record) {
                controller.set('errors', record.get('errors'));
            });
            wallPost.save();
        }
    },

    createNewWallPost: function() {
        this.set('model', App.TextWallPost.createRecord());
    }
});


App.MediaWallPostNewController = App.TextWallPostNewController.extend({

    // This a temporary container for App.Photo records until they are connected after this wall-post is saved.
    files: Em.A(),

    createNewWallPost: function() {
        this.set('model', App.MediaWallPost.createRecord());
    },

    actions: {
        saveWallPost: function() {
            var store = this.get('store');
            var wallPost = this.get('model');
            var controller = this;

            wallPost.set('parent_id', this.get('parentId'));
            wallPost.set('parent_type', this.get('type'));
            wallPost.set('type', 'media');

            wallPost.on('didCreate', function(record) {
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
                    var list = controller.get('wallPostList');
                    list.unshiftObject(record);
                    controller.createNewWallPost()
                });
            });
            wallPost.on('becameInvalid', function(record) {
                controller.set('errors', record.get('errors'));
            });
            wallPost.save();
        }
    },

    addFile: function(file) {
        var store = this.get('store');
        var photo = store.createRecord(App.WallPostPhoto);
        // Connect the file to it. DRF2 Adapter will sort this out.
        photo.set('photo', file);
        photo.save();
        var controller = this;
        // Store the photo in this.files. We need to connect it to the wallpost later.
        photo.on('didCreate', function(record){
            controller.get('files').pushObject(photo);
        });
    },

    removePhoto: function(photo) {
        photo.deleteRecord();
        photo.save();
        // Remove it from temporary array too.
        this.get('files').removeObject(photo);
    }

});


/* Task WallPosts */

App.TaskWallPostMixin = Em.Mixin.create({

    needs: ['currentUser', 'projectTask', 'projectTaskIndex'],
    type: 'task',

    parentId: function(){
        return this.get('controllers.projectTask.model.id');
    }.property('controllers.projectTask.model.id'),

    wallPostList: function(){
        return this.get('controllers.projectTaskIndex.model');
    }.property('controllers.projectTaskIndex.model')

})

App.TaskTextWallPostNewController = App.TextWallPostNewController.extend(App.TaskWallPostMixin, {});
App.TaskMediaWallPostNewController = App.MediaWallPostNewController.extend(App.TaskWallPostMixin, {});


/* Project WallPosts */

App.ProjectWallPostMixin = Em.Mixin.create({

    needs: ['currentUser', 'project', 'projectIndex'],
    type: 'project',

    parentId: function(){
        return this.get('controllers.project.model.id');
    }.property('controllers.project.model.id'),

    wallPostList: function(){
        return this.get('controllers.projectIndex.model');
    }.property('controllers.projectIndex.model')
})

App.ProjectTextWallPostNewController = App.TextWallPostNewController.extend(App.ProjectWallPostMixin, {});
App.ProjectMediaWallPostNewController = App.MediaWallPostNewController.extend(App.ProjectWallPostMixin, {});


/* FundRaiser WallPosts */

App.FundRaiserWallPostMixin = Em.Mixin.create({

    needs: ['currentUser', 'fundRaiser', 'fundRaiserIndex'],
    type: 'fundraiser',

    parentId: function(){
        return this.get('controllers.fundRaiser.model.id');
    }.property('controllers.fundRaiser.model.id'),

    wallPostList: function(){
        return this.get('controllers.fundRaiserIndex.model');
    }.property('controllers.fundRaiserIndex.model')
});

App.FundRaiserTextWallPostNewController = App.TextWallPostNewController.extend(App.FundRaiserWallPostMixin, {});
App.FundRaiserMediaWallPostNewController = App.MediaWallPostNewController.extend(App.FundRaiserWallPostMixin, {});


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
