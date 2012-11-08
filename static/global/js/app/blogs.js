App.Blog = DS.Model.extend({
    url: 'blogs',
    slug: DS.attr('string'),
    title: DS.attr('string'),
    contents: DS.attr('string'),
    author: DS.belongsTo('App.Member', {embedded: true}),
    author_name: function(){
        var auth = this.get('author');
        
        return'yeah ' + auth.first_name;
    }.property('author')
    
});


App.blogListController = App.ListController.create({
    model: App.Blog,
});


App.blogDetailController = App.DetailController.create({
    model: App.Blog,
});

App.BlogHeaderView = Em.View.extend({
    templateName: 'blog_header',
    templateFile: 'blog_list',
    classNames: ['container', 'black'],
    
});



App.BlogDetailView = Em.View.extend({
    contentBinding: 'App.blogDetailController',
    templateName: 'blog_detail',
    classNames: ['container'],
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

