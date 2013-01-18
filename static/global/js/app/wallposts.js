
/*
 Models
 */

App.MediaWallPostPhoto = DS.Model.extend({
    photo: DS.attr('string'),
    thumbnail: DS.attr('string')
});

// This is union of all different wallposts.
App.ProjectWallPost = DS.Model.extend({
    url: 'projects/wallposts',

    // Model fields
    project_id: DS.attr('number'),
    author: DS.belongsTo('App.Member', {embedded: true}),
    title: DS.attr('string'),
    text: DS.attr('string'),
    created: DS.attr('string'),
    timesince: DS.attr('string'),
    video_url: DS.attr('string'),
    video_html: DS.attr('string'),
    photo: DS.attr('string'),
    photos: DS.hasMany('App.MediaWallPostPhoto', {embedded: true}),
    reactions: DS.hasMany('App.Reaction', {embedded: true}),

    didCreate: function(record) {
        // record will be a subclass of ProjectWallPost (e.g. ProjectMediaWallPost).
        App.projectWallPostListController.get('content').unshiftObject(record);
    }
});


App.ProjectMediaWallPost = App.ProjectWallPost.extend({
    url: 'projects/wallposts/media',
    type: 'media'
});

App.ProjectTextWallPost = App.ProjectWallPost.extend({
    url: 'projects/wallposts/text',
    type: 'text'
});


/*
 Controllers
 */

App.projectWallPostListController = Em.ArrayController.create({

    // The list of WallPosts are loaded into a temporary array when the project changes. Once this RecordArray is
    // loaded, it is converted to an Ember array and put into content. This temporary array is required because
    // the RecordArray returned by findQuery can't be manipulated directly. Discussion about this can be found in
    // these two pages:
    // http://stackoverflow.com/questions/11895629/add-delete-items-from-ember-data-backed-arraycontroller
    // https://github.com/emberjs/data/issues/370
    projectBinding: "App.projectDetailController.content",

    projectChanged: function(sender, key) {
        var projectId = this.get('project.id');
        this.set('wallposts', App.ProjectWallPost.find({project_id: projectId}));
    }.observes('project'),

    wallpostsLoaded: function(sender, key) {
        if (this.get(key)) {
            this.set('content', this.get('wallposts').toArray());
        }
    }.observes('wallposts.isLoaded'),

    // This Ember object is used as a placeholder for the WallPost object so that Em.get/set always work.
    wallpostForm: new Em.Object(),

    // Add the project_id whenever the wallpost model is updated.
    wallpostFormChanged: function(sender, key) {
        this.get(key).set('project_id', this.get('project.id'));
    }.observes('wallpostForm'),

    addWallPost: function() {
        App.store.commit();
    }
});




/*
 Views
 */

App.WallPostFormContainerView = Em.View.extend({
    templateName: 'wallpost_form_container',
    templateFile: 'wallpost',

    classNames: ['container', 'section'],
    contentBinding: "App.projectDetailController.content",

    isOwner: function() {
        var user = this.get('user');
        var owner = this.get('content.owner'); 
        if (user && owner && user.get('username')) {
            return user.get('username') == owner.get('username');
        }
        return false;
    }.property('user', 'content.owner')
});


App.MediaWallPostFormView = Em.View.extend({
    templateName: 'media_wallpost_form',
    templateFile: 'wallpost',
    tagName: 'form',

    wallpostBinding: 'App.projectWallPostListController.wallpostForm',

    init: function() {
        this._super();
        this.set('controller', App.MediaWallPostFormController);
        this.set('wallpost', App.ProjectMediaWallPost.createRecord());
    },

    submit: function(e){
        e.preventDefault();
        App.projectWallPostListController.addWallPost();
    },

    // Create a new wallpost when it's been successfully saved to the server (isNew == false).
    wallpostChanged: function(sender, key) {
        if (!this.get(key)) {
            this.set('wallpost', App.ProjectMediaWallPost.createRecord());
        }
    }.observes('wallpost.isNew')
});


App.MediaWallPostFormController = Em.ObjectController.create({
//    transaction: App.store.transaction(),

    contentBinding: 'App.MediaWallPostFormView.wallpost',

    init: function() {
        this._super();
//        this.set('content', this.get('transaction').createRecord(model, wallpost));
    },

    addWallPost: function() {
        console.log('bork');
//        this.get('transaction').commit();
    },

    contentChanged: function(sender, key) {
//        if (!this.get(key)) {
//            this.set('wallpost', App.ProjectMediaWallPost.createRecord());
//        }
        console.log('borka olkasdjhf lasdkjhf ');
    }.observes('content.isNew')
});


App.TextWallPostFormView = Em.View.extend({
    templateName: 'text_wallpost_form',
    templateFile: 'wallpost',
    tagName: 'form',

    wallpostBinding: 'App.projectWallPostListController.wallpostForm',

    init: function() {
        this._super();
        this.set('wallpost', App.ProjectTextWallPost.createRecord());
    },

    submit: function(e){
        e.preventDefault();
        App.projectWallPostListController.addWallPost();
    },

    // Create a new wallpost when it's been successfully saved to the server (isNew == false).
    wallpostChanged: function(sender, key) {
        if (!this.get(key)) {
            this.set('wallpost', App.ProjectTextWallPost.createRecord());
        }
    }.observes('wallpost.isNew')
});


App.UploadFileView = Ember.TextField.extend({
    type: 'file',
    attributeBindings: ['name', 'accept'],

    wallpostBinding: 'App.projectWallPostListController.wallpostForm',

    change: function(e) {
        var input = e.target;
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            var that = this;
            reader.onload = function(e) {
                that.get('wallpost').set('photo', e.target.result);
            }
            reader.readAsDataURL(input.files[0]);
            this.get('wallpost').set('photo_file', input.files[0]);
        }
    }
});


App.WallPostFormTipView = Em.View.extend({
    tagName: 'article',
    classNames: ['sidebar', 'tip', 'not-implemented'],
    templateName: 'wallpost_form_tip',
    templateFile: 'wallpost'
});


App.WallPostView = Em.View.extend({
    tagName: 'article',
    classNames: ['wallpost'],
    templateName: 'wallpost',
    templateFile: 'wallpost',
    isAuthor: function(){
        var username = this.get('user.username');
        var authorname = this.get('content.author.username');
        if (username) {
            return (username == authorname);
        }
        return false;
    }.property('user', 'content'), 
    deleteWallPost: function(e) {
        if (confirm("Delete this wallpost?")) {
            e.preventDefault();
            var post = this.get('content');
            // Clear author here
            // TODO: Have a proper solution for belongsTo fields in adapter
            post.reopen({
                author: null
            });
            post.deleteRecord();
            App.store.commit();
            var self = this;
            this.$().slideUp(1000, function(){self.remove();});
        }
    }
});


App.ProjectWallPostListView = Em.CollectionView.extend({
    tagName: 'section',
    classNames: ['wrapper'],
    contentBinding: 'App.projectWallPostListController',
    itemViewClass: 'App.WallPostView'
});
