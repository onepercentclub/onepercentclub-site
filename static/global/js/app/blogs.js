App.blogListController = App.ListController.create({
    content: null,
    dataUrl: 'blogs/',
    filterParams: {'order':'-created'},
});


App.blogDetailController = App.DetailController.create({
    content: null,
    dataUrl: 'blogs/',
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

