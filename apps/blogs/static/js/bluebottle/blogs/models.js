/**
 * Embedded mappings
 */

App.Adapter.map('App.News', {
    author: {embedded: 'load'}
});


/**
 * Models
 */

App.News = DS.Model.extend({
    url: 'blogs/news',
    slug: DS.attr('string'),
    title: DS.attr('string'),
    body: DS.attr('string'),
    publicationDate: DS.attr('date'),
    author: DS.belongsTo('App.UserPreview')
});

App.NewsPreview = DS.Model.extend({
    url: 'blogs/preview/news',
    slug: DS.attr('string'),
    title: DS.attr('string'),
    publicationDate: DS.attr('date')
});

