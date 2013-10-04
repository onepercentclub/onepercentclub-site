/*
 Models
 */

App.ProjectWallPostPhoto = DS.Model.extend({
    url: 'projects/wallposts/media/photos',
    photo: DS.attr('image'),
    mediawallpost: DS.belongsTo('App.ProjectWallPost')
});



// This is union of all different wallposts.
App.WallPost = DS.Model.extend({
    url: 'wallposts',

    // Model fields
    author: DS.belongsTo('App.UserPreview'),
    title: DS.attr('string'),
    text: DS.attr('string'),
    type: DS.attr('string'),
    created: DS.attr('date'),
    reactions: DS.hasMany('App.WallPostReaction'),

    video_url: DS.attr('string'),
    video_html: DS.attr('string'),
    photos: DS.hasMany('App.ProjectWallPostPhoto'),

    isSystemWallPost: function(){
        return (this.get('type') == 'system');
    }.property('type')
});


App.ProjectWallPost = App.WallPost.extend({
    url: 'projects/wallposts',
    project: DS.belongsTo('App.Project')
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
            var list = controller.get('controllers.projectIndex.items');
            list.unshiftObject(record);
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
    }
});


App.SystemWallPostView = Em.View.extend({
    templateName: 'system_wallpost'
});


App.ProjectWallPostView = Em.View.extend({
    templateName: 'project_wallpost',

    didInsertElement: function(){
        // Give it some time to really render...
        // Hack to make sure photo viewer works for new wallposts
        Em.run.later(function(){
            this.$('.gallery-picture').colorbox({
                rel: this.toString(),
                next: '<span class="flaticon solid right-2"></span>',
                previous: '<span class="flaticon solid left-2"></span>',
                close: '×'
            });
        }, 500);
    },

    actions: {
        deleteWallPost: function() {
            var view = this;
            var wallpost = this.get('controller.model');
            Bootstrap.ModalPane.popup({
                heading: gettext("Really?"),
                message: gettext("Are you sure you want to delete this comment?"),
                primary: gettext("Yes"),
                secondary: gettext("Cancel"),
                callback: function(opts, e) {
                    e.preventDefault();
                    if (opts.primary) {
                        view.$().fadeOut(500, function() {
                            wallpost.deleteRecord();
                            wallpost.save();
                        });
                    }
                }
            });
        }
    }

});


App.TaskWallPostView = App.ProjectWallPostView.extend({
    templateName: 'task_wallpost'

});

// This is the view toi display the wallpost list
// Idea of how to have child views with different templates:
// http://stackoverflow.com/questions/10216059/ember-collectionview-with-views-that-have-different-templates
App.ProjectIndexView = Em.View.extend({
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

