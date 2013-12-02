App.Slide = DS.Model.extend({
    url: 'banners',

    title: DS.attr('string'),
    body: DS.attr('string'),
    image: DS.attr('string'),
    imageBackground: DS.attr('string'),
    video: DS.attr('string'),

    language: DS.attr('string'),
    style: DS.attr('string'),
    sequence: DS.attr('number'),
    style: DS.attr('string'),
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

App.HomePage = DS.Model.extend({
    url: 'homepage',

    projects: DS.hasMany('App.ProjectPreview'),
    slides: DS.hasMany('App.Slide'),
    quotes: DS.hasMany('App.Quote'),
    impact: DS.belongsTo('App.Impact'),
    campaign: DS.belongsTo('App.Campaign'),
    fundraisers: DS.hasMany('App.FundRaiser')

});

App.Adapter.map('App.HomePage', {
    projects: {embedded: 'load'},
    slides: {embedded: 'load'},
    quotes: {embedded: 'load'},
    impact: {embedded: 'load'},
    campaign: {embedded: 'load'},
    fundraisers: {embedded: 'load'}
});


/* Controllers */

App.HomeController = Ember.ObjectController.extend({
    needs: ['currentUser'],

    isCampaignHomePage: false,

    nextProject: function() { // TODO: similar thing for fundraisers?
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
        }
    },

    actions: {
        scrollToFundraisers: function() {
            var offset = $('#home-crazy-campaign-fundraisers').offset().top;
            $("html, body").animate({ scrollTop: offset }, 600);
        }
    }
});

/* Views */

App.HomeBannerView = Ember.View.extend({
    templateName: 'home_banner',

    didInsertElement: function() {
    
        // Carousel
        this.$().find('.carousel').unslider({
            dots: true,
            fluid: true,
            delay: 10000
        });
    }
});


App.HomeProjectView = Ember.View.extend({
    templateName: 'home_project',

    didInsertElement: function() {
        var donated = this.get('controller.project.campaign.money_donated');
        var asked = this.get('controller.project.campaign.money_asked');
        this.$('.slider-progress').css('width', '0px');
        var width = 0;
        if (asked > 0) {
            width = 100 * donated / asked;
            width += '%';
        }
        this.$('.slider-progress').animate({'width': width}, 1000);
    }.observes('controller.project')
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

function go(){
    $(document).bind("keydown", function(e){

        var trackOffset = $('#track').offset().left;
        if (e.keyCode == 71) {
            $('#car1').css({'left' : "+=5px"});
        }
        if (e.keyCode == 80) {
            $('#car2').css({'left' : "+=5px"});
        }

        if (($('#car2').offset().left - trackOffset) >= 1060) {
            $('#race').html("Great race! You'd be a great fund-racer too!");
            $('.message-board').css({'background-color': '#FF619A', 'color': 'white'});
            $(document).unbind("keydown");
            $('.message-board').html('PINK WINS!');
        }
        if (($('#car1').offset().left - trackOffset) >= 1060) {
            $('#race').html("Great race! You'd be a great fund-racer too!");
            $('.message-board').css({'background-color': '#00C051', 'color': 'white'});
            $(document).unbind("keydown");
            $('.message-board').html('GREEN WINS!');
        }
    });
}

var time = 10;
function countdown() {

    $('.message-board').html(time);
    if (time<=0) {
        $('.message-board').removeClass('digit');
        $('.message-board').html('GO');
        go();
    } else {
        setTimeout('countdown()', 1000);
    }
    time--;
}


App.HomeCampaignView = Ember.View.extend({
    templateName: 'home_campaign_block',
    
    didInsertElement: function() {
    
        // Countdown for campaign
        var deadline = this.get('controller.campaign.end');
        
        this.$().find('#countdown').countdown({
            until: deadline,
            format: 'HMS',
            whichLabels: null,
            timeSeparator: ':',
            layout: $('#countdown').html()
        });

        var html = '<section class="l-wrapper"><div class="hasCountdown"><span class="message-board"></span></div><h3 id="race">[P] for Pink, [G] for Green</h3><h4>Ready to race? </h4><div id="track"><div id="start"></div><div id="finish"></div><div id="car1"></div><div id="car2"></div></div></section>';

        var typeKeys = [67, 82, 65, 90, 89];
        var something_index = 0;

        $(document).bind("keydown", function (e) {
            if (e.keyCode === typeKeys[something_index++]) {
                if (something_index === typeKeys.length) {
                    $('#home-crazy-campaign-header').html(html);
                    $('.message-board').html('Get ready!');
                    setTimeout('countdown()', 2000);
                }
            } else {
                something_index = 0;
            }
        });

    }
});
