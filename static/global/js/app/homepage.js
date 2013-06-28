App.Banner = DS.Model.extend({
    url: 'banners',

    title: DS.attr('string'),
    body: DS.attr('string'),
    image: DS.attr('string'),
    imageUrl: function() {
        return '/static/media/' + this.get('image');
    }.property('image'),
    language: DS.attr('string'),
    sequence: DS.attr('number'),
    tab_text: DS.attr('string'),
    link_text: DS.attr('string'),
    link_url: DS.attr('string'),
    isFirst: function() {
        var sequence = this.get('sequence');
        return (sequence === 0);
    }.property('sequence')
});


App.Quote = DS.Model.extend({
    url: 'quotes',

    quote: DS.attr('string'),
    segment: DS.attr('string'),
    user: DS.belongsTo('App.UserPreview')
});


App.Impact = DS.Model.extend({
    url: 'stat',

    lives_changed: DS.attr('number'),
    projects: DS.attr('number'),
    countries: DS.attr('number'),
    hours_spent: DS.attr('number'),
    donated: DS.attr('number')
});


App.HomeController = Ember.Controller.extend({
    needs: ['currentUser'],

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
    }
});


App.HomeBannerView = Ember.View.extend({
    templateName: 'home_banner',

    didInsertElement: function() {
        this.$().find('#bannerCarousel').unslider({
            dots: true,
            delay: 10000
        });
    }
});


App.HomeProjectView = Ember.View.extend({
    templateName: 'home_project'
});


App.HomeQuotesView = Ember.View.extend({
    templateName: 'home_quotes',

    didInsertElement: function() {
        var controller = this.get('controller');

        Ember.run.later(this, function() {
            this.initQuoteCycle();
        }, 5000);
    },

    initQuoteCycle: function() {
        var controller = this.get('controller');
        var view = this;

        var quoteIntervalId = setInterval(function() {
            controller.incrementProperty('quoteIndex');
            if (controller.get('quoteIndex') === controller.get('quotes').get('length')) {
                controller.set('quoteIndex', 0);
            }

            controller.loadQuote();

            var $activeBtn = view.$('.btn:not(.disabled)');
            $activeBtn.addClass('disabled');

            var $nextBtn = $activeBtn.next('.btn');
            $nextBtn = ($nextBtn.length) ? $nextBtn : $activeBtn.prevAll('.btn').last();
            $nextBtn.removeClass('disabled');
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


