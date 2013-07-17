/* Models */

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

/* Controller */

App.NewsController = Em.ArrayController.extend({

    page: 1,

    // TODO: be smarter then this! Calculate hasNext.
    hasNext: true,
    hasPrevious: function(){
        return this.get('page') > 1;
    }.property('page'),



    previousNews: function(){
        var controller = this;
        this.decrementProperty('page');
        var page = this.get('page');
        if (page > 0) {
            var news  =  App.NewsPreview.find({language: App.get('language'), page: page});
            news.one('didLoad', function(){
                //controller.get('model').addObjects(news);
                controller.set('model', news);
            });
        }
    },
    nextNews: function(){
        var controller = this;
        this.incrementProperty('page');
        var page = this.get('page');
        var news  =  App.NewsPreview.find({language: App.get('language'), page: page});
        news.one('didLoad', function(){
            //controller.get('model').addObjects(news);
            controller.set('model', news);
        });
    }
})


/* Views */

App.NewsItemView = Em.View.extend({
    templateName: 'news_item'
});

App.NewsIndexView = Em.View.extend({
    templateName: 'news_index'
});


App.NewsItemPreviewView = Em.View.extend({
    templateName: 'news_item_preview'
});

App.NewsView = Em.View.extend({
    templateName: 'news'
});

