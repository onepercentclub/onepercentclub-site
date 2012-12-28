
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
App.ProjectMediaWallPost = DS.Model.extend({
    url: 'wallposts/projectmediawallposts',

    // Model fields
    // Should we be using DS.belongsTo here?
    project_id: DS.attr('number'),
    author: DS.belongsTo('App.Member', {embedded: true}),
    title: DS.attr('string'),
    text: DS.attr('string'),
    video_url: DS.attr('string'),
    timesince: DS.attr('string'),
    video_html: DS.attr('string'),

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
        // Add project_id to the wallpost
        wallpost.project_id = this.get('content.query.project_id');
        this.get('model').createRecord(wallpost);
        App.store.commit()
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


App.WallPostFormView = Em.View.extend({
    templateName: 'wallpost_form',
    templateFile: 'wallpost',
    tagName: 'form',
    wallpost: {},
    submit: function(e){
        e.preventDefault();
        App.projectWallPostListController.addMediaWallPost(this.get('wallpost'));
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
