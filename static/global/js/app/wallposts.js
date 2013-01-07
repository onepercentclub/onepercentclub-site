
/*
 Models
 */

// This is union of all different wallposts
// TODO: see if we can teach Ember Data to use a combined list of all wallposts
App.ProjectWallPost = DS.Model.extend({
    url: 'wallposts/projectwallposts',

    // Model fields
    project_id: DS.attr('number'),
    author: DS.belongsTo('App.Member', {embedded: true}),
    title: DS.attr('string'),
    text: DS.attr('string'),
    created: DS.attr('string'),
    timesince: DS.attr('string'),
    video_url: DS.attr('string'),
    video_html: DS.attr('string'),

    // TODO: Find a better way to refresh the list
    didCreate: function() {
        App.store.find(App.ProjectWallPost, this.get('id'));
        App.projectWallPostListController.set('content', App.store.all(App.ProjectWallPost));
    }

});


App.ProjectMediaWallPost = App.ProjectWallPost.extend({
    url: 'wallposts/projectmediawallposts'

});

App.ProjectTextWallPost = App.ProjectWallPost.extend({
    url: 'wallposts/projecttextwallposts'
});


/*
 Controllers
 */

App.projectWallPostListController = Em.ArrayController.create({
    // Use store transactions so we set the model properly and don't start with an empty '{}'...
    models: {
        'media': App.ProjectMediaWallPost,
        'text': App.ProjectTextWallPost
    },
    
    projectBinding: "App.projectDetailController.content",
    
    content: function(){
        if (this.get('project.id')) {
            return App.ProjectWallPost.find({project_id: this.get('project.id')})
        }
    }.property('project'),

    addWallPost: function(wallpost) {
        // Load the right model based on type
        var model = this.get('models.' + wallpost.type);
        // If we have a standard object then convert into the right model
        if (!(wallpost instanceof model)) {
            // Add project_id to the wallpost
            wallpost.project_id = this.get('project.id');
            var wallpost = model.createRecord(wallpost);
        } 
        App.store.commit();
        // Return the model (with errors) for the form to return it to the user.
        return wallpost;
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
    canEdit: function() {
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
    wallpost: {type: 'media'},
    submit: function(e){
        e.preventDefault();
        // Send the object to controller
        // This will return a DS.Model with optional error codes
        var wallpost = App.projectWallPostListController.addWallPost(this.get('wallpost'));
        // For now always return true so we get the errors
        // TODO: Find out how we can properly check for errors
        if (1 || wallpost.errors) {
            // We'll replace this.wallpost with the proper DS.Model to bind errors
            this.set('wallpost', wallpost);
        } else {
            // Wallpost was created succesfully so clear the form:
            this.set('wallpost', {type: wallpost.type});
        }
    }
});


App.TextWallPostFormView = App.MediaWallPostFormView.extend({
    templateName: 'text_wallpost_form',
    wallpost: {type: 'text'},
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
        var username = this.get('user').get('username');
        var authorname = this.get('content').get('author').get('username');
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
            })
            post.deleteRecord();
            App.store.commit()
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
