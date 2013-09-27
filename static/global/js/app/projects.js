/*
 Models
 */


App.Organization = DS.Model.extend({
    url: 'organizations',
    name: DS.attr('string'),
    description: DS.attr('string', {defaultValue: ""}),

    // Internet
    website: DS.attr('string', {defaultValue: ""}),
    facebook: DS.attr('string', {defaultValue: ""}),
    twitter: DS.attr('string', {defaultValue: ""}),
    skype: DS.attr('string', {defaultValue: ""}),

    // Legal
    legalStatus: DS.attr('string', {defaultValue: ""})
});


App.ProjectCountry = DS.Model.extend({
    name: DS.attr('string'),
    subregion: DS.attr('string')
});


App.ProjectPitch = DS.Model.extend({
    url: 'projects/pitches',

    project: DS.belongsTo('App.MyProject'),
    created: DS.attr('date'),
    status: DS.attr('string'),

    // Basics
    title: DS.attr('string'),
    pitch: DS.attr('string'),
    theme: DS.attr('string'),
    tags: DS.hasMany('App.Tag'),
    description: DS.attr('string'),
    need: DS.attr('string'),

    // Location
    country: DS.belongsTo('App.ProjectCountry'),
    latitude: DS.attr('string'),
    longitude: DS.attr('string'),

    // Media
    image: DS.attr('string'),
    image_small: DS.attr('string'),
    image_square: DS.attr('string'),
    image_bg: DS.attr('string')

});


App.ProjectPlan = DS.Model.extend({
    url: 'projects/plans',

    project: DS.belongsTo('App.MyProject'),
    status: DS.attr('string'),
    created: DS.attr('date'),

    // Basics
    title: DS.attr('string'),
    pitch: DS.attr('string'),
    theme: DS.belongsTo('App.Theme'),
    need: DS.attr('string'),
    tags: DS.hasMany('App.Tag'),

    // Description
    description: DS.attr('string'),
    effects: DS.attr('string'),
    future: DS.attr('string'),
    for_who: DS.attr('string'),
    reach: DS.attr('number'),

    // Location
    country: DS.belongsTo('App.ProjectCountry'),
    latitude: DS.attr('string'),
    longitude: DS.attr('string'),

    // Media
    image: DS.attr('image'),

    // Organization
    organization: DS.belongsTo('App.Organization')

});


App.ProjectCampaign = DS.Model.extend({
    url: 'projects/plans',

    project: DS.belongsTo('App.MyProject'),
    status: DS.attr('string'),
    money_asked: DS.attr('number'),
    money_donated: DS.attr('number'),
    deadline: DS.attr('date'),

    daysToGo: function(){
        var now = new Date();
        var microseconds = this.get('deadline').getTime() - now.getTime();
        return Math.ceil(microseconds / (1000 * 60 * 60 * 24));
    }.property('deadline'),

    money_needed: function(){
        var donated = this.get('money_asked') - this.get('money_donated');
        if (donated < 0) {
            return 0;
        }
        return Math.ceil(donated);
    }.property('money_asked', 'money_donated')
});


App.Project = DS.Model.extend({
    url: 'projects/projects',

    // Model fields
    slug: DS.attr('string'),
    title: DS.attr('string'),
    phase: DS.attr('string'),
    created: DS.attr('date'),

    plan: DS.belongsTo('App.ProjectPlan'),
    campaign: DS.belongsTo('App.ProjectCampaign'),

    owner: DS.belongsTo('App.UserPreview'),
    coach: DS.belongsTo('App.UserPreview'),

    days_left: DS.attr('number'),
    supporters_count: DS.attr('number'),

    wallposts: DS.hasMany('App.WallPost'),

    taskCount: DS.attr('number'),

    isPhasePlan: Em.computed.equal('phase', 'plan'),
    isPhaseCampaign: Em.computed.equal('phase', 'campaign'),
    isPhaseAct: Em.computed.equal('phase', 'act'),
    isPhaseResults: Em.computed.equal('phase', 'results'),
    isPhaseRealized: Em.computed.equal('phase', 'realized'),
    isPhaseFailed: Em.computed.equal('phase', 'failed'),

    getProject: function(){
        return App.Project.find(this.get('id'));
    }.property('id')


});


App.ProjectPreview = App.Project.extend({
    url: 'projects/previews',
    image: DS.attr('string'),
    country: DS.belongsTo('App.ProjectCountry')
});


App.ProjectSearch = DS.Model.extend({

    text: DS.attr('string'),
    country: DS.attr('number'),
    theme:  DS.attr('number'),
    ordering: DS.attr('string', {defaultValue: 'popularity'}),
    phase: DS.attr('string', {defaultValue: 'campaign'}),
    page: DS.attr('number', {defaultValue: 1})

});


App.DonationPreview =  DS.Model.extend({
    url: 'projects/donations',

    project: DS.belongsTo('App.ProjectPreview'),
    member: DS.belongsTo('App.UserPreview'),
    date_donated: DS.attr('date'),

    time_since: function(){
        return Globalize.format(this.get('date_donated'), 'X');
    }.property('date_donated')
});


/*
 Controllers
 */

App.ProjectListController = Em.ArrayController.extend({
    needs: ['projectSearchForm']
});


App.ProjectSearchFormController = Em.ObjectController.extend({
    needs: ['projectList'],

    init: function(){
        var form =  App.ProjectSearch.createRecord();
        this.set('model', form);
        this.updateSearch();
    },

    rangeStart: function(){
        return this.get('page') * 8 -7;
    }.property('controllers.projectList.model.length'),

    rangeEnd: function(){
        return this.get('page') * 8 -8 + this.get('controllers.projectList.model.length');
    }.property('controllers.projectList.model.length'),

    hasNextPage: function(){
        var next = this.get('page') * 8;
        var total = this.get('controllers.projectList.model.meta.total');
        return (next < total);
    }.property('controllers.projectList.model.meta.total'),

    hasPreviousPage: function(){
        return (this.get('page') > 1);
    }.property('page'),

    nextPage: function(){
        this.incrementProperty('page');
    },

    previousPage: function(){
        this.decrementProperty('page');
    },

    sortOrder: function(order) {
        this.set('ordering', order);
    },

    orderedByPopularity: function(){
        return (this.get('ordering') == 'popularity');
    }.property('ordering'),
    orderedByTitle: function(){
        return (this.get('ordering') == 'title');
    }.property('ordering'),
    orderedByNewest: function(){
        return (this.get('ordering') == 'newest');
    }.property('ordering'),
    orderedByNeeded: function(){
        return (this.get('ordering') == 'needed');
    }.property('ordering'),
    orderedByDeadline: function(){
        return (this.get('ordering') == 'deadline');
    }.property('ordering'),

    clearForm: function(sender, key) {
        this.set('model.text', '');
        this.set('model.country', null);
        this.set('model.theme', null);
        this.set('model.phase', null);
    },

    updateSearch: function(sender, key){
        if (key != 'page') {
            // If the query changes we should jump back to page 1
            this.set('page', 1);
        }
        if (this.get('model.isDirty') ) {
            var list = this.get('controllers.projectList');
            var controller = this;

            var query = {
                'page': this.get('page'),
                'ordering': this.get('ordering'),
                'phase': this.get('phase'),
                'country': this.get('country'),
                'text': this.get('text'),
                'theme': this.get('theme')
            };
            var projects = App.ProjectPreview.find(query);
            list.set('model', projects);
        }
    }.observes('text', 'country', 'theme', 'phase', 'page', 'ordering')
});


App.ProjectController = Em.ObjectController.extend({
    isFundable: function(){
       return (this.get('phase') == 'campaign' && this.get('campaign.money_asked'));
    }.property('phase', 'campaign'),

    allTags: function() {
        var tags = this.get('plan.tags');

        return tags.reduce(function(previousValue, tag, index) {
            var separator = (index == 0 ? " " : ", ");
            return previousValue + separator + tag.id;
        }, "");
    }.property('tags.@each')

});


App.ProjectSupporterListController = Em.ArrayController.extend({
    supportersLoaded: function(sender, key) {
        if (this.get(key)) {
            this.set('model', this.get('supporters').toArray());
        } else {
            // Don't show old content when new content is being retrieved.
            this.set('model', null);
        }
    }.observes('supporters.isLoaded')

});


/*
 Views
 */

App.AnimateProgressMixin = Em.Mixin.create({
    didInsertElement: function(){
        var donated = this.get('controller.campaign.money_donated');
        var asked = this.get('controller.campaign.money_asked');
        this.$('.donate-progress').css('width', '0px');
        var width = 0;
        if (asked > 0) {
            width = 100 * donated / asked;
            width += '%';
        }
        this.$('.donate-progress').animate({'width': width}, 1000);
    }
});

App.ProjectMembersView = Em.View.extend({
    templateName: 'project_members'
});

App.ProjectSupporterView = Em.View.extend({
    templateName: 'project_supporter',
    tagName: 'li',
    didInsertElement: function(){
        this.$('a').popover({trigger: 'hover', placement: 'top', width: '100px'})
    }
});


App.ProjectSupporterListView = Em.View.extend({
    templateName: 'project_supporter_list'
});


App.ProjectListView = Em.View.extend({
    templateName: 'project_list'
});

App.ProjectPreviewView = Em.View.extend(App.AnimateProgressMixin, {
    templateName: 'project_preview'
});


App.ProjectSearchFormView = Em.View.extend({
    templateName: 'project_search_form'
});


App.ProjectPlanView = Em.View.extend({
    templateName: 'project_plan',

    staticMap: function(){
        var latlng = this.get('controller.latitude') + ',' + this.get('controller.longitude');
        return "http://maps.googleapis.com/maps/api/staticmap?" + latlng + "&zoom=8&size=600x300&maptype=roadmap" +
            "&markers=color:pink%7Clabel:P%7C" + latlng + "&sensor=false";
    }.property('latitude', 'longitude')
});


App.ProjectView = Em.View.extend(App.AnimateProgressMixin, {
    templateName: 'project',

    didInsertElement: function(){
        this._super();
        this.$('.tags').popover({trigger: 'hover', placement: 'top', width: '100px'});
    }
});

/**
 * Generic view to plug-in social sharing functionality anywhere in the app.
 * e.g. {{view App.SocialShareView classNames="your-styling-class-name"}}
 *
 * Gets the entire current URL to share.
 * TODO: Move somewhere else suitable.
 *
 * @class SocialShareView
 * @namespace App
 * @extends Ember.View
 */
App.SocialShareView = Em.View.extend({
    templateName: 'social_share',
    dialogW: 626,
    dialogH: 436,

    shareOnFacebook: function() {
        this.showDialog('https://www.facebook.com/sharer/sharer.php?u=', 'facebook');
    },

    shareOnTwitter: function() {
        this.showDialog('https://twitter.com/home?status=', 'twitter');
    },

    showDialog: function(shareUrl, type) {
        var currentLink = encodeURIComponent(location.href);

        window.open(shareUrl + currentLink, type + '-share-dialog', 'width=' + this.get('dialogW') + ',height=' + this.get('dialogH'));
    }
})

/*
 Form Elements
 */


App.ProjectOrderList = [
    {value: 'title', title: "title"},
    {value: 'money_needed', title: "money needed"},
    {value: 'deadline', title: "deadline"}
];

App.ProjectOrderSelectView = Em.Select.extend({
    content: App.ProjectOrderList,
    optionValuePath: "content.value",
    optionLabelPath: "content.title"
});

App.ProjectPhaseList = [
    {value: 'plan', title: gettext("Writing Plan")},
    {value: 'campaign', title: gettext("Campaign")},
    {value: 'act', title: gettext("Act")},
    {value: 'results', title: gettext("Results")},
    {value: 'realized', title: gettext("Realised")}
];

App.ProjectPhaseSelectView = Em.Select.extend({
    content: App.ProjectPhaseList,
    optionValuePath: "content.value",
    optionLabelPath: "content.title",
    prompt: gettext("Pick a phase")

});


