App.Adapter.map('App.MyProject', {
    tags: {embedded: 'load'},
    budgetLines: {embedded: 'load'}
});

App.Project.reopen({

    deadline: DS.attr('date'),
    amount_asked: DS.attr('number'), //, {defaultValue: 0}),
    allowOverfunding: DS.attr('boolean'),

    maxAmountAsked: Ember.computed.lte('amount_asked', 1000000),
    minAmountAsked: Ember.computed.gte('amount_asked', 250),

    amount_donated: DS.attr('number', {defaultValue: 0}),
    amount_needed: DS.attr('number', {defaultValue: this.get('amount_asked')}),

    fundraisers: DS.belongsTo('App.Fundraiser'),

    task_count: DS.attr('number'),

    isFundable: Em.computed.equal('status.id', '5'),

    isStatusPlan: Em.computed.lt('status.id', '5'),
    isStatusCampaign: Em.computed.equal('status.id', '5'),
    isStatusCompleted: Em.computed.equal('status.id', '7'),
    isStatusStopped: Em.computed.gt('status.id', '9'),

    isSupportable: function () {
        var now = new Date();
        return this.get('isStatusCampaign') && this.get('deadline') > now && (this.get('amount_needed') > 0 || this.get('allowOverfunding'));
    }.property('isStatusCampaign', 'deadline', 'amount_needed', 'allowOverfunding'),

    save: function () {
        // the amount_needed is calculated here and not in the server
        this.set('amount_needed', this.get('calculatedAmountNeeded'));
        
        this._super();
    }

});


App.MyProjectBudgetLine = DS.Model.extend({
    url: 'bb_projects/budgetlines',

    project: DS.belongsTo('App.MyProject'),
    description: DS.attr('string'),
    amount: DS.attr('number')
});


App.MyProject.reopen({
    image: DS.attr('image'),
    video: DS.attr('string'),
    budgetLines: DS.hasMany('App.MyProjectBudgetLine'),
    story: DS.attr('string'),

    defaultStory: gettext("<h3>Introduction of your campaign</h3><p>We’ve already set some structure in this plan, but you are free to write it in your own way.</p><h3>What are you going to do?</h3><p>Remember to keep a logic structure, use headings, paragraphs.</p><h3>How are you going to achieve that?</h3><p>Keep it short and sweet!</p>"),
    storyChanged: function () {
        return Em.compare(this.get('defaultStory'), this.get('story'));
    }.property('story'),

    budgetTotal: function(){
        var lines = this.get('budgetLines');
        return lines.reduce(function(prev, line){
            return (prev || 0) + (line.get('amount')/1 || 0);
        });
    }.property('budgetLines.@each.amount'),

    init: function () {
        this._super();

        // If no story set then set to the default
        if (!this.get('story'))
            this.set('story', this.get('defaultStory'));

        this.validatedFieldsProperty('validGoal', this.get('requiredGoalFields'));
        this.missingFieldsProperty('missingFieldsGoal', this.get('requiredGoalFields'));
    },

    valid: Em.computed.and('validStory', 'validPitch', 'validGoal', 'organization.isLoaded', 'organization.valid'),

    requiredStoryFields: ['story', 'storyChanged'],
    requiredGoalFields: ['amount_asked', 'deadline', 'maxAmountAsked', 'minAmountAsked'],
    requiredPitchFields: ['title', 'pitch', 'image', 'theme', 'tags.length', 'country', 'latitude', 'longitude'],

    friendlyFieldNames: {
        'title' : 'Title',
        'pitch': 'Description',
        'storyChanged' : 'Personalised story',
        'image' : 'Image',
        'theme' : 'Theme',
        'tags.length': 'Tags',
        'deadline' : 'Deadline',
        'country' : 'Country',
        'description': 'Why, what and how',
        'goal' : 'Goal',
        'destination_impact' : 'Destination impact'
    }

});



