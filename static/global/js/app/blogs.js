App.blogListController = App.ListController.create({
    dataUrl: 'blogs/',
});


App.blogDetailController = App.DetailController.create({
    dataUrl: 'blogs/',
});

App.BlogHeaderView = Em.View.extend({
    templateName: 'blog_header',
    templateFile: 'blog_list'
    
});



App.BlogDetailView = Em.View.extend({
    contentBinding: 'App.blogDetailController',
    templateName: 'blog_detail',
    classNames: ['lightgreen', 'section'],
});

App.BlogPreviewView = Em.View.extend({
    templateName: 'blog_preview',
    templateFile: 'blog_list'
    
});

App.BlogNoItemsView = Em.View.extend({
    templateName: 'blog_no_items',
    templateFile: 'blog_list'
    
});


App.BlogListView = Em.CollectionView.extend({
    tagName: 'ul',
    contentBinding: 'App.blogListController.content',
    emptyViewClass: 'App.BlogNoItemsView',
    itemViewClass: 'App.BlogPreviewView',
});

