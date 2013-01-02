
/*
 Models
 */

App.ProjectWallPost = DS.Model.extend({
    url: 'wallposts/projectwallposts',

    // Model fields
    project_id: DS.attr('number'),
    author: DS.belongsTo('App.Member', {embedded: true}),
    title: DS.attr('string'),
    text: DS.attr('string'),
    timesince: DS.attr('string'),
    video_url: DS.attr('string'),
    video_html: DS.attr('string'),

    // TODO: (how) do we want to use this??
    didCreate: function() {
        App.store.find(App.ProjectWallPost, this.get('id'));
        App.projectWallPostListController.set('content', App.store.all(App.ProjectWallPost));
    }

});


// Temporary model for projectmediawallposts list/create.
App.ProjectMediaWallPost = App.ProjectWallPost.extend({
    url: 'wallposts/projectmediawallposts',

});

// Temporary model for projectmediawallposts list/create.
App.ProjectTextWallPost = App.ProjectWallPost.extend({
    url: 'wallposts/projecttextwallposts',
});


/*
 Controllers
 */

App.projectWallPostListController = Em.ArrayController.create({
    models: {
        'media': App.ProjectMediaWallPost,
        'text': App.ProjectTextWallPost
    },
    projectIdChanged: function(sender, key) {
        var projectId = App.projectDetailController.get('content').get('id')
        this.set('content', App.ProjectWallPost.find({project_id: projectId}));
    }.observes('App.projectDetailController.content'),


    addWallPost: function(wallpost) {
        var model = this.get('models.'+wallpost.type);
        // TODO: Why is this called when the project page is first loaded? 
        // Loek says: Is it?
        
        // If we have a standard object then convert into the right model
        if (!(wallpost instanceof model)) {
            // Add project_id to the wallpost
            wallpost.project_id = this.get('content.query.project_id');
            var wallpost = model.createRecord(wallpost);
        } 
        App.store.commit();
        // TODO: Make sure the wallpost lists gets updated if the post was successful
        
        // Return the model (with errors) for the form to parse it.
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
        // We'll replace this.wallpost with the proper DS.Model to bind errors
        this.set('wallpost',  App.projectWallPostListController.addWallPost(this.get('wallpost')));
    }
});

App.TextWallPostFormView = Em.View.extend({
    templateName: 'text_wallpost_form',
    templateFile: 'wallpost',
    tagName: 'form',
    wallpost: {type: 'text'},
    submit: function(e){
        e.preventDefault();
        // Send the object to controller
        // This will return a DS.Model with optional error codes
        // We'll replace this.wallpost with the proper DS.Model to bind errors
        this.set('wallpost',  App.projectWallPostListController.addWallPost(this.get('wallpost')));
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
        var username = this.get('user').get('username');
        var authorname = this.get('content').get('author').get('username');
        if (username) {
            return (username == authorname);
        }
        return false;
    }.property('user', 'content'), 
    editWallPost: function(e) {
        //alert("About to edit wallpost:\n" + this.get('content.text'));
        var post = this.get('content');
        console.log(post);
        App.TextWallPostFormView.set('wallpost', post);
        App.MediaWallPostFormView.set('wallpost', post);
        e.preventDefault();
        
    },
    deleteWallPost: function(e) {
        alert("About to delete wallpost:\n" + this.get('content.text'));
        e.preventDefault();
        var post = this.get('content');
        // Clear author here
        // TODO: Have a proper solution for belongsTo fields in adapter
        post.reopen({
            author: null
        })
        post.deleteRecord();
        App.store.commit()
        
    }
});


App.ProjectWallPostListView = Em.CollectionView.extend({
    tagName: 'section',
    classNames: ['wrapper'],
    contentBinding: 'App.projectWallPostListController',
    itemViewClass: 'App.WallPostView'
});
