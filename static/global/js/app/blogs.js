/* Models */

App.News = DS.Model.extend({
    url: 'blogs/posts',
    slug: DS.attr('string'),
    title: DS.attr('string'),
    body: DS.attr('string'),
    publicationDate: DS.attr('date'),
    author: DS.belongsTo('App.UserPreview')
});

App.NewsPreview = DS.Model.extend({
    url: 'blogs/previews',
    slug: DS.attr('string'),
    title: DS.attr('string'),
    publicationDate: DS.attr('date')
});

/* Controller */


/* Views */

App.NewsView = Em.View.extend({
    templateName: 'news_item'
});

App.NewsItemPreviewView = Em.View.extend({
    templateName: 'news_item_preview',
    templateFile: 'blog_list'
    
});

App.NewsListView = Em.View.extend({
    templateName: 'news_list',
    emptyViewClass: 'App.BlogNoItemsView',
    itemViewClass: 'App.BlogPreviewView'
});

