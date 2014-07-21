
App.HomeController = Ember.ObjectController.extend({
    init: function(){
        this._super();
         if (this.get('tracker')) {
            // The homepage event is only logged once, when the user visits the homepage for the first time
            // in a session. A session means that the user vists the website without hard page reloads
            this.get('tracker').trackEvent("Homepage", {});
        }
    },
    project: null,
    isCampaignHomePage: false,
    projectIndex: 0,
    quoteIndex: 0,
    actions: {
        nextProject: function() {
            this.incrementProperty('projectIndex');
        },
    
        prevProject: function() {
            this.decrementProperty('projectIndex');        
        }        
    },
    
    animateSlider: function() {
        var index = this.get('projectIndex');
        var project_count = this.get("projects").get("length");
        $(".project-slides").animate({'margin-left': -(1100 * (index % project_count))})
    }.observes('projectIndex'),

    loadQuote: function() {
        this.set('quote', this.get('quotes').objectAt(this.get('quoteIndex')));
    }
});
