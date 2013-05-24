/*
 Models
 */

App.ProjectWallPostPhoto = DS.Model.extend({
    url: 'projects/wallposts/media/photos',

    photo: DS.attr('string'),
    thumbnail: DS.attr('string'),
    mediawallpost: DS.belongsTo('App.ProjectWallPost')
});



// This is union of all different wallposts.
App.WallPost = DS.Model.extend({
    url: 'wallposts',

    // Model fields
    author: DS.belongsTo('App.MemberPreview'),
    title: DS.attr('string'),
    text: DS.attr('string'),
    created: DS.attr('date'),
    reactions: DS.hasMany('App.WallPostReaction')
});


App.ProjectWallPost = App.WallPost.extend({
    url: 'projects/wallposts',

    project: DS.belongsTo('App.Project'),

    video_url: DS.attr('string'),
    video_html: DS.attr('string'),
    photos: DS.hasMany('App.ProjectWallPostPhoto'),

});


App.NewProjectWallPost = App.ProjectWallPost.extend({
    url: 'projects/wallposts'
});

App.ProjectMediaWallPost = App.ProjectWallPost.extend({
    url: 'projects/wallposts/media'
});

App.ProjectTextWallPost = App.ProjectWallPost.extend({
    url: 'projects/wallposts/text'
});


App.TaskWallPost = App.WallPost.extend({
    url: 'tasks/wallposts',

    task: DS.belongsTo('App.Task')
});

/*
 Controllers
 */

App.ProjectWallPostListController = Em.ArrayController.extend({
    // Make sure this is an array controller


});

App.TaskWallPostListController = Em.ArrayController.extend({
    needs: ['currentUser']
});

App.ProjectWallPostNewController = Em.ObjectController.extend({
    // TODO: Find out how we can reference the instance of ProjectWallPostList
    needs: ['currentUser', 'project_wallPostList', 'project'],

    // This a temporary container for App.Photo records until they are connected after this wallpost is saved.
    files: Em.A(),

    init: function() {
        this._super();
        this.set('content', App.NewProjectWallPost.createRecord());
    },

    addMediaWallPost: function() {
        var transaction = this.get('store').transaction();
        var mediawallpost = transaction.createRecord(App.ProjectMediaWallPost);
        mediawallpost.set('title', this.get('content.title'));
        mediawallpost.set('text', this.get('content.text'));
        mediawallpost.set('video_url', this.get('content.video_url'));
        mediawallpost.set('project', this.get('controllers.project.model'));

        var controller = this;
        // As soon as the wallpost has got an id we can start connecting photos to it.
        mediawallpost.addObserver('id', function(){
            if (controller.get('files').length) {
                // Start a new transaction and add the wallpost and all the photos to it.
                var transaction = controller.get('store').transaction();
                // Add the wallpost to the same transaction.
                transaction.add(mediawallpost);
                var reload = true;
                controller.get('files').forEach(function(photo){
                    transaction.add(photo);
                    // Connect a photo to the new wallpost.
                    photo.set('mediawallpost', mediawallpost);
                    photo.on('didUpdate', function(){
                        if (reload) {
                            mediawallpost.reload();
                            reload = false;
                        }
                    });
                });
                // Empty this.files so we can use it again.
                controller.set('files', Em.A());
                transaction.commit();
            }
        });

        mediawallpost.on('didCreate', function(record) {
            // Target is a reference to ParentWallPostList (e.g. the parent controller)
            controller.get('target').unshiftObject(record);
            controller.clearWallPost()
        });
        mediawallpost.on('becameInvalid', function(record) {
            controller.set('errors', record.get('errors'));
//            TODO: The record needs need to be deleted somehow.
//            record.deleteRecord();
        });
        transaction.commit();
    },

    addFile: function(file) {
        var transaction = this.get('store').transaction();
        var photo = transaction.createRecord(App.ProjectWallPostPhoto);
        // Connect the file to it. DRF2 Adapter will sort this out.
        photo.set('file', file);
        this.get('files').pushObject(photo);
        transaction.commit();
        // Store the photo in this.files. We need to connect it to the wallpost later.
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
            controller.get('target').unshiftObject(record);
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


App.ProjectWallPostController = Em.ObjectController.extend(App.IsAuthorMixin, {
    needs: ['currentUser', 'wallPostReactionList', 'wallPostReactionNew'],

    reactionsChanged: function(sender, key) {
        this.set('controllers.wallPostReactionList.content', this.get('content.reactions'))
    }.observes('content.reactions.length'),

    // This is acting like a binding.
    wallpostIdChanged: function(sender, key) {
        this.set('controllers.wallPostReactionNew.currentWallpost', this.get('content'))
    }.observes('content', 'controllers.wallPostReactionNew.currentWallpost'),

    deleteRecordOnServer: function(){
        var transaction = this.get('store').transaction();
        var model = this.get('model');
        transaction.add(model);
        model.deleteRecord();
        transaction.commit();
    }
});



App.TaskWallPostController = Em.ObjectController.extend(App.IsAuthorMixin, {
    needs: ['currentUser', 'wallPostReactionList', 'wallPostReactionNew'],

    reactionsChanged: function(sender, key) {
        this.set('controllers.wallPostReactionList.content', this.get('content.reactions'))
    }.observes('content.reactions.length'),

    // This is acting like a binding.
    wallpostIdChanged: function(sender, key) {
        this.set('controllers.wallPostReactionNew.currentWallpost', this.get('content'))
    }.observes('content', 'controllers.wallPostReactionNew.currentWallpost'),

    deleteRecordOnServer: function(){
        var transaction = this.get('store').transaction();
        var model = this.get('model');
        transaction.add(model);
        model.deleteRecord();
        transaction.commit();
    }
});


App.TaskWallPostNewController = Em.ObjectController.extend({
    // TODO: See how we can reference Task and TaskWallPostList controllers
    needs: ['currentUser', 'task_wallPostList', 'project_task'],
    init: function() {
        this._super();
        var task = this.get('controllers.project_task');
        var transaction = this.get('store').transaction();
        var wallPost = transaction.createRecord(App.TaskWallPost);
        this.set('content', wallPost);
    },
    addTextWallPost: function() {
        var controller = this;
        var wallpost = this.get('content');
        // Parent-parent controller is the task
        var task = this.get('target.target');
        wallpost.set('task', task);
        wallpost.on('didCreate', function(record) {
            controller.get('target').unshiftObject(record);
            // Init again to set up a new model for the form.
            controller.init();
        });
        wallpost.on('becameInvalid', function(record) {
            controller.set('errors', record.get('errors'));
//            TODO: The record needs need to be deleted somehow.
//            record.deleteRecord();
        });
        wallpost.transaction.commit();
    }

});

/*
 Views
 */

App.MediaWallPostNewView = Em.View.extend({
    templateName: 'media_wallpost_new',
    tagName: 'form',

    submit: function(e) {
        e.preventDefault();
        this.get('controller').addMediaWallPost();
    },

    didInsertElement: function() {
        this.get('controller').clearWallPost();
        this.$('label.inline').inFieldLabels();
    }
});


App.TextWallPostNewView = Em.View.extend({
    templateName: 'text_wallpost_new',
    tagName: 'form',

    submit: function(e){
        e.preventDefault();
        this.get('controller').addTextWallPost();
    },

    didInsertElement: function() {
        this.get('controller').clearWallPost();
        this.$('label.inline').inFieldLabels();
    }
});


App.UploadFileView = Ember.TextField.extend({
    type: 'file',
    attributeBindings: ['name', 'accept'],

    contentBinding: 'parentView.controller.content',

    change: function(e) {
        var controller = this.get('controller');
        var files = e.target.files;
        for (i = 0; i < files.length; i++) {
            var reader = new FileReader();
            var file = files[i];
            // TODO: enable client site previews with: reader.onload = function(e){}
            reader.readAsDataURL(file);
            this.get('controller').addFile(file);
        }
        // Clear the input field after uploading.
        e.target.value = null;
    }
});


App.ProjectWallPostView = Em.View.extend({
    templateName: 'project_wallpost',

    didInsertElement: function(){
        this.$('.gallery-picture').colorbox({rel: this.toString()});
    },

    // TODO: Delete reactions to WallPost as well?
    deleteWallPost: function() {
        var view = this;

        Bootstrap.ModalPane.popup({
            heading: "Really?",
            message: "Are you sure you want to delete this comment?",
            primary: "Yes",
            secondary: "Cancel",
            callback: function(opts, e) {
                e.preventDefault();
                if (opts.primary) {
                    view.$().fadeOut(500, function() {
                        view.get('controller').deleteRecordOnServer()
                    });
                }
            }
        });
    }
});


App.TaskWallPostView = App.ProjectWallPostView.extend({
    templateName: 'task_wallpost'

});

// Idea of how to have child views with different templates:
// http://stackoverflow.com/questions/10216059/ember-collectionview-with-views-that-have-different-templates
App.ProjectWallPostListView = Em.View.extend({
    templateName: 'project_wallpost_list'
});


App.ProjectWallPostNewView = Em.View.extend({
    templateName: 'project_wallpost_new'
});


App.TaskWallPostListView = Em.View.extend({
    templateName: 'task_wallpost_list'

});


App.TaskWallPostNewView = Em.View.extend({
    templateName: 'task_wallpost_new',
    tagName: 'form'
});

