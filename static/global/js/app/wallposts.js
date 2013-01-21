
/*
 Models
 */

App.MediaWallPostPhoto = DS.Model.extend({
    photo: DS.attr('string'),
    thumbnail: DS.attr('string'),
    projectwallpost: DS.belongsTo('App.ProjectWallPost')
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
    reactions: DS.hasMany('App.WallPostReaction', {embedded: true})
});


App.ProjectMediaWallPost = App.ProjectWallPost.extend({
    url: 'projects/wallposts/media'
});

App.ProjectTextWallPost = App.ProjectWallPost.extend({
    url: 'projects/wallposts/text'
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

    addMediaWallPost: function(mediawallpost) {
        var transaction = App.store.transaction();
        var livemediawallpost = transaction.createRecord(App.ProjectMediaWallPost, mediawallpost.toJSON());
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

    addTextWallPost: function(textwallpost) {
        var transaction = App.store.transaction();
        var livetextwallpost = transaction.createRecord(App.ProjectTextWallPost, textwallpost.toJSON());
        livetextwallpost.set('project_id', this.get('project.id'));
        livetextwallpost.on('didCreate', function(record) {
            App.projectWallPostListController.get('content').unshiftObject(record);
            textwallpost.set('text', '');
            textwallpost.set('errors', null);
        });
        livetextwallpost.on('becameInvalid', function(record) {
            textwallpost.set('errors', record.get('errors'));
        });
        transaction.commit();
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

    wallpost: App.ProjectMediaWallPost.createRecord(),

    submit: function(e){
        e.preventDefault();
        App.projectWallPostListController.addMediaWallPost(this.get('wallpost'));
    }
});


App.TextWallPostFormView = Em.View.extend({
    templateName: 'text_wallpost_form',
    templateFile: 'wallpost',
    tagName: 'form',

    wallpost: App.ProjectTextWallPost.createRecord(),

    submit: function(e){
        e.preventDefault();
        App.projectWallPostListController.addTextWallPost(this.get('wallpost'));
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
            var transaction = App.store.transaction();
            var post = this.get('content');
            transaction.add(post);
            // Clear author here
            // TODO: Have a proper solution for belongsTo fields in adapter
            post.reopen({
                author: null,
                reactions: []
            });
            post.deleteRecord();
            transaction.commit();
            var self = this;
            this.$().slideUp(500, function(){self.remove();});
        }
    }
});


App.ProjectWallPostListView = Em.CollectionView.extend({
    tagName: 'section',
    classNames: ['wrapper'],
    contentBinding: 'App.projectWallPostListController',
    itemViewClass: 'App.WallPostView'
});

