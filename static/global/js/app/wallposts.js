

App.WallPost = DS.Model.extend({
    url: 'wallposts',

    // Model fields
    author: DS.belongsTo('App.Member', {embedded: true}),
    title: DS.attr('string'),
    text: DS.attr('string'),
    timesince: DS.attr('string'),
    video_html: DS.attr('string')
});


App.wallPostListController = App.ListController.create({
    model: App.WallPost,

    getList: function(filterParams){
        var slug = filterParams['slug'];
        var type = filterParams['type'];
        var url =  type + '/' + slug + '/wallposts/';
        var model =  this.get('model');
        model.reopen({
            'url': url
        });
        this.set('content', App.store.findAll(model));
    }
});


App.WallPostView = Em.View.extend({
    templateName: 'wallpost',
    templateFile: 'wallpost'
});