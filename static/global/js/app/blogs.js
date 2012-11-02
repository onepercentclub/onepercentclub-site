/*
 * Project Detail
 */
App.blogModel = Em.Object.create({});

App.blogSearchController = Em.ObjectController.create({
    content: null,
    populate: function(slug){
        var controller = this;
        require(['app/data_source'], function(){
            App.dataSource.get('blogs/' + slug, {}, function(data) {
                controller.set('content', data);
            });
        })
    }
});

App.blogDetailController = Em.ObjectController.create({
    content: null,
    get: function(slug){
        var controller = this;
        require(['app/data_source'], function(){
            App.dataSource.get('blogs/' + slug, {}, function(data) {
                controller.set('content', data);
            });
        })
    }
});



App.BlogDetailView = Em.View.extend({
    contentBinding: 'App.blogDetailController',
    templateName: 'blog_detail',
    classNames: ['lightgreen', 'section'],
});

App.BlogSearchView = Em.View.extend({
    contentBinding: 'App.blogSearchController',
    templateName: 'blog_search',
    classNames: ['lightgreen', 'section'],
});

