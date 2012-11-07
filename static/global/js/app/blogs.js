App.Blog = DS.Model.extend({
    url: DS.attr('string'),
    slug: DS.attr('string'),
    title: DS.attr('string'),
    contents: DS.attr('string'),
    
});


App.blogListController = App.ListController.create({
    model: App.Blog,
});


App.blogDetailController = App.DetailController.create({
    model: App.Blog,
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

