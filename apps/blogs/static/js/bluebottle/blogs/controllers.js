App.NewsController = Em.ObjectController.extend({});


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
});
