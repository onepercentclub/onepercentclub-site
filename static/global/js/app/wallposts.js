
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
    video_html: DS.attr('string')
});


// Temporary model for projectmediawallposts list/create.
App.ProjectMediaWallPost = App.ProjectWallPost.extend({
    url: 'wallposts/projectmediawallposts',

    // TODO: (how) do we want to use this??
    didCreate: function() {
        console.log('greate');
    },
    becameError: function() {
        console.log('bork');
    }
});


/*
 Controllers
 */

App.projectWallPostListController = Em.ArrayController.create({
    model: App.ProjectMediaWallPost,

    projectIdChanged: function(sender, key) {
        var projectId = App.projectDetailController.get('content').get('id')
        this.set('content', App.ProjectWallPost.find({project_id: projectId}));
    }.observes('App.projectDetailController.content'),

    addMediaWallPost: function(wallpost) {
        // TODO: Why is this called when the project page is first loaded?
        // If we have a standard object then convert into the right model
        if (!(wallpost instanceof this.get('model'))) {
            // Add project_id to the wallpost
            wallpost.project_id = this.get('content.query.project_id');
            var wallpost = this.get('model').createRecord(wallpost);
        } 
        App.store.commit();
        // Return the model (with errors) for the form to parse it.
        return wallpost;
        // TODO: Deal with the response when wallpost is created - it returns the newly created WallPost.
    }
});


/*
 Views
 */

App.WallPostFormContainerView = Em.View.extend({
    templateName: 'wallpost_form_container',
    templateFile: 'wallpost',
    classNames: ['container', 'section']
});


App.MediaWallPostFormView = Em.View.extend({
    templateName: 'media_wallpost_form',
    templateFile: 'wallpost',
    tagName: 'form',
    wallpost: {},
    submit: function(e){
        e.preventDefault();
        // Send the object to controller
        // This will return a DS.Model with optional error codes
        // We'll replace this.wallpost with the proper DS.Model to bind errors
        this.set('wallpost',  App.projectWallPostListController.addMediaWallPost(this.get('wallpost')));
    }
});

App.TextWallPostFormView = Em.View.extend({
    templateName: 'text_wallpost_form',
    templateFile: 'wallpost',
    tagName: 'form',
    wallpost: {},
    submit: function(e){
        e.preventDefault();
        App.projectWallPostListController.addTextWallPost(this.get('wallpost'));
    }
});


App.WallPostView = Em.View.extend({
    tagName: 'article',
    classNames: ['wallpost'],
    templateName: 'wallpost',
    templateFile: 'wallpost'
});


App.ProjectWallPostListView = Em.CollectionView.extend({
    tagName: 'section',
    classNames: ['wrapper'],
    contentBinding: 'App.projectWallPostListController',
    itemViewClass: 'App.WallPostView'
});
