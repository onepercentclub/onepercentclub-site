App.HomeBannerView = Ember.View.extend({
    templateName: 'home_banner',

    didInsertElement: function() {

        // Carousel
        var banner = $('.home-carousel .carousel').unslider({
                dots: true,
                fluid: true,
                delay: 8000
            }), _this = this,
            unsliderData = banner.data('unslider'),
            iframe = $('#brand-video'),
            player = $f(iframe),
            animationEnd = 'animationEnd animationend webkitAnimationEnd oAnimationEnd MSAnimationEnd';
     
        setTimeout(function() {
         $(".home-carousel .home-carousel-nav span:first-child").addClass("is-active");   
        }, 200);

        this.$().find('.video-play-btn').on('mouseenter', function(){
            $(".video-item-content").addClass("is-blur");
        });

        this.$().find('.video-play-btn').on('mouseleave', function(){
            $(".video-item-content").removeClass("is-blur");
        });

        this.$().find('.video-play-btn').on('click', function(){
            $(".video-item").removeClass("is-inactive");
            $(".video-item").addClass("is-active");
            unsliderData.stop();
            player.api("play");
        });

        this.$().find('.close-video').on('click', function(){
            $(".video-item").removeClass("is-active");
            $(".video-item").addClass("is-inactive");
            player.api("pause");

            $('.video-item').one(animationEnd, function(){
                $(".video-item").removeClass("is-inactive");
            });
        });

        function onFinish(id) {
            $(".video-item").removeClass("is-active");
            $(".video-item").addClass("is-inactive");

            $('.video-item').one(animationEnd, function(){
                $(".video-item").removeClass("is-inactive");
                unsliderData.start();
            });
        }
        
        function onPlayProgress(data, id) {
            unsliderData.stop();
        }
        
        player.addEvent('ready', function() {
            player.addEvent('finish', onFinish);
            player.addEvent('playProgress', onPlayProgress);
        });

        // TODO: Make it a general Ember component
        var heightHead = $('.home-carousel-content h1').height();

        if (heightHead > 100) {
            $('.home-carousel .first-item').addClass('dutch-head');
        }
    }
});


App.QuoteCarouselView = Em.View.extend({
    templateName: 'quote_carousel',

    didInsertElement: function() {
        var quoteSlider = $('#quote-carousel').unslider({
                dots: false,
                fluid: true,
                delay: 8000,
                keys: false
            }), _this = this,
            data = quoteSlider.data('unslider');


        this.$().find('.previous').on('click', function(e){
            e.preventDefault();
            data.prev();
            _this.send('didInsertElement');
        });

        this.$().find('.next').on('click', function(e){
            e.preventDefault();
            data.next();
            _this.send('didInsertElement');
        });
    }
})


App.HomeProjectListView = Ember.View.extend({
    index: 0,
    templateName: 'home_project_list',
	
    didInsertElement: function() {
        var controller = this.get('controller');
        var projects_count = $(".project-preview").size();
        $(".project-slides").width(projects_count * 1100);
    }
});


App.HomeQuotesView = Ember.View.extend({
    templateName: 'home_quotes',

    didInsertElement: function() {
        var controller = this.get('controller');
        this.initQuoteCycle();
    },

    initQuoteCycle: function() {
        var controller = this.get('controller');
        var view = this;
        
        controller.loadQuote();
        
        
        var quoteIntervalId = setInterval(function() {
            controller.incrementProperty('quoteIndex');
            if (controller.get('quoteIndex') === controller.get('quotes').get('length')) {
                controller.set('quoteIndex', 0);
            }
        
            controller.loadQuote();
        
        }, 5000);
        
        this.set('quoteIntervalId', quoteIntervalId);
    },

    willDestroyElement: function() {
        clearInterval(this.get('quoteIntervalId'));
        this.set('quoteIntervalId', null);
    }
});


App.HomeImpactView = Ember.View.extend({
    templateName: 'home_impact'
});


App.HomeFundraisersView = Ember.View.extend({
    templateName: 'home_fundraisers'
});

App.HomeBusinessView = Ember.View.extend({
    templateName: 'business_block'
})

