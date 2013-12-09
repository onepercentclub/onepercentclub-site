App.GroupPageBannerView = Ember.View.extend({
    templateName: 'home_banner',

    didInsertElement: function() {

        // Carousel
        this.$().find('.carousel').unslider({
            height: 450,
            dots: true,
            fluid: true,
            delay: 10000
        });
    }
});


App.GroupView = Em.View.extend({
    didInsertElement: function(){
        this.$('a').popover({trigger: 'hover', placement: 'top'})
    }
});