/* Models */

App.News = DS.Model.extend({
    url: 'blogs',
    slug: DS.attr('string'),
    title: DS.attr('string'),
    body: DS.attr('string'),
    publicationDate: DS.attr('date'),
    author: DS.belongsTo('App.UserPreview')
});


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

