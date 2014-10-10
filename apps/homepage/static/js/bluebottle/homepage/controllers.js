
App.HomeController = Ember.ObjectController.extend({
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
        },
        goToFavouriteProject: function(project) {
//            if (this.get('tracker')) {
//                this.get('tracker').trackEvent("Click Favourite Project", {title: project.get("title")});
//            }
            this.transitionToRoute('project', project);
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
