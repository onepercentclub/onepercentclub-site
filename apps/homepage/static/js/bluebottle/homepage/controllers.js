

/* Controllers */

App.HomeController = Ember.ObjectController.extend({
    needs: ['currentUser'],

    isCampaignHomePage: false,

    nextProject: function() {
        var projects = this.get('projects');

        this.incrementProperty('projectIndex');

        if (this.get('projectIndex') >= projects.get('length')) {
            this.set('projectIndex', 0);
        }

        this.loadProject();
    },

    previousProject: function() {
        var projects = this.get('projects');

        this.decrementProperty('projectIndex');

        if (this.get('projectIndex') < 0) {
            this.set('projectIndex', projects.get('length') - 1);
        }

        this.loadProject();
    },

    loadProject: function() {
        var controller = this;
        var projectId = this.get('projects').objectAt(this.get('projectIndex')).get('id');
        App.Project.find(projectId).then(function(project) {
            controller.set('project', project);
        });
    },

    loadQuote: function() {
        this.set('quote', this.get('quotes').objectAt(this.get('quoteIndex')));
    },

    checkCampaignHomePage: function() {
        if(this.get('campaign')){
            this.set('isCampaignHomePage', true);
            var finished = this.get('fundraisers').filterBy('is_funded', true).length;
            this.set('finishedFundraiserCount', finished);
        }
    },

    actions: {
        scrollToFundraisers: function() {
            var offset = $('#home-crazy-campaign-fundraisers').offset().top;
            $("html, body").animate({ scrollTop: offset }, 600);
        }
    }
});
