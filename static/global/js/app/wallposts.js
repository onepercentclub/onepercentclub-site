

App.ProjectWallPost = DS.Model.extend({
    url: 'wallposts/projectwallposts',

    // Model fields
    author: DS.belongsTo('App.Member', {embedded: true}),
    title: DS.attr('string'),
    text: DS.attr('string'),
    timesince: DS.attr('string'),
    video_html: DS.attr('string')
});


App.projectWallPostListController = Em.ArrayController.create({
    model: App.ProjectWallPost,

    projectIdChanged: function(sender, key) {
        var projectId = App.projectDetailController.get('content').get('id')
        this.set('content', App.ProjectWallPost.find({project_id: projectId}));
    }.observes('App.projectDetailController.content')
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
