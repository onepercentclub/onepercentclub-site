App.loadTemplates(['wallposts']);


/*
 Models
 */

App.MediaWallPostPhoto = DS.Model.extend({
    photo: DS.attr('string'),
    thumbnail: DS.attr('string'),
});

// This is union of all different wallposts.
App.Projectwallpost = DS.Model.extend({
    url: 'projects/wallposts',

    // Model fields
    project_id: DS.attr('number'),
    author: DS.belongsTo('App.Member'),
    title: DS.attr('string'),
    text: DS.attr('string'),
    created: DS.attr('string'),
    timesince: DS.attr('string'),
    video_url: DS.attr('string'),
    video_html: DS.attr('string'),
    photo: DS.attr('string'),
    photos: DS.hasMany('App.MediaWallPostPhoto'),
    reactions: DS.hasMany('App.WallPostReaction')
});


App.ProjectMediaWallPost = App.Projectwallpost.extend({
    url: 'projects/wallposts/media'
});

App.ProjectTextWallPost = App.Projectwallpost.extend({
    url: 'projects/wallposts/text'
});


/*
 Controllers
 */




App.WallPostControllerMixin = Em.Mixin.create({

    deleteWallPost: function(update_ui_callback) {
        var wallpost = this.get('content');
        wallpost.deleteRecord();
        App.store.commit();
        wallpost.on('didDelete', function() {
            update_ui_callback();
        });
    },

//    isAuthor: function() {
//        var username = this.get('user.username');
//        var authorname = this.get('content.author.username');
//        if (username) {
//            return (username == authorname);
//        }
//        return false;
//    }.property('user', 'content')

});

App.ProjectwallpostsController = Em.ArrayController.extend(App.WallPostControllerMixin, {

    isOwner: function() {
        var user = this.get('user');
        var owner = this.get('content.owner');
        if (user && owner && user.get('username')) {
            return user.get('username') == owner.get('username');
        }
        return false;
    }.property('user', 'content.owner')

});


App.ProjectwallpostNewController = Em.ObjectController.extend({

    content: App.Projectwallpost.createRecord(),

    addMediaWallPost: function(mediawallpost) {
        var transaction = App.store.transaction();
        var livemediawallpost = transaction.createRecord(App.ProjectMediaWallPost, mediawallpost);
        livemediawallpost.set('project_id', this.get('project.id'));
        livemediawallpost.set('photo_file', mediawallpost.get('photo_file'));
        livemediawallpost.on('didCreate', function(record) {
            App.projectWallPostListController.get('content').unshiftObject(record);
            mediawallpost.set('title', '');
            mediawallpost.set('text', '');
            mediawallpost.set('video_url', '');
            mediawallpost.set('photo', '');
            mediawallpost.set('photo_file', null);
            mediawallpost.set('errors', null);
        });
        livemediawallpost.on('becameInvalid', function(record) {
            mediawallpost.set('errors', record.get('errors'));
        });
        transaction.commit();
    },

    addTextWallPost: function() {
        var transaction = App.store.transaction();
        var textwallpost = transaction.createRecord(App.ProjectTextWallPost);
        textwallpost.set('text', this.get('content.text'));
        textwallpost.set('project_id', this.get('currentProject.id'));
        var controller = this;
        textwallpost.on('didCreate', function(record) {
            controller.get('projectwallpostsController.content').unshiftObject(record);
            controller.clearWallPost()
        });
        textwallpost.on('becameInvalid', function(record) {
            controller.set('content.errors', record.get('errors'));
        });
        transaction.commit();
    },

    clearWallPost: function() {
        this.set('content.text', '');
        this.set('content.errors', null);
    }

});


/*
 Views
 */

App.MediaWallPostFormView = Em.View.extend({
    templateName: 'media_wallpost_form',
    tagName: 'form',

    wallpost: App.ProjectMediaWallPost.createRecord(),

    submit: function(e){
        e.preventDefault();
        this.get('controller').addMediaWallPost();
    }
});


App.TextWallPostFormView = Em.View.extend({
    templateName: 'text_wallpost_form',
    tagName: 'form',

    submit: function(e){
        e.preventDefault();
        this.get('controller').addTextWallPost();
    },

    didInsertElement: function() {
        this.get('controller').clearWallPost();
    }

});


App.UploadFileView = Ember.TextField.extend({
    type: 'file',
    attributeBindings: ['name', 'accept'],

    wallpostBinding: 'parentView.wallpost',

    change: function(e) {
        var input = e.target;
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            var view = this;
            reader.onload = function(e) {
                // This should really be saved someplace else.
                view.get('wallpost').set('photo_preview', e.target.result);
            }
            reader.readAsDataURL(input.files[0]);
            // The File object needs to be set on the Model so that it can be accesses in the DRF2 adapter.
            this.get('wallpost').set('photo_file', input.files[0]);
        }
    }
});


App.WallPostFormTipView = Em.View.extend({
    tagName: 'article',
    classNames: ['sidebar', 'tip', 'not-implemented'],
    templateName: 'wallpost_form_tip'
});


App.ProjectwallpostView = Em.View.extend({
    templateName: 'projectwallpost'
});


// child views different templates
// http://stackoverflow.com/questions/10216059/ember-collectionview-with-views-that-have-different-templates
App.ProjectwallpostsView = Em.View.extend({
    templateName: 'projectwallposts'
});


App.WallPostDeleteButton = Em.View.extend({
    click: function(e) {
        if (confirm("Delete this wallpost?")) {
            this.get('controller').deleteWallPost(function(){
                var self = this;
                this.$().slideUp(1000, function(){self.remove();});
            });
        }
    }
});
