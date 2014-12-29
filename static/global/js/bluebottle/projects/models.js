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
    partner: DS.belongsTo('App.Partner'),

    mchanga_account: DS.attr('string'),

    task_count: DS.attr('number'),

    donatedRound: function() {
        return Math.floor(this.get('amount_donated'));
    }.property(),

    phaseNum: function(){
        if (this.get('status') === null){
            return 1;
        }
        return parseInt(this.get('status.id'));
    }.property('status.id'),

    isFundable: Em.computed.equal('phaseNum', 5),

    isStatusPlan: Em.computed.lt('phaseNum', 5),
    
    isStatusCampaign: Em.computed.equal('phaseNum', 5),
    
    isStatusCompleted: Em.computed.equal('phaseNum', 7),
    
    isStatusStopped: Em.computed.gt('phaseNum', 9),

    isSupportable: function () {
        var now = new Date();
        return this.get('isStatusCampaign') && this.get('deadline') > now && (this.get('amount_needed') > 0 || this.get('allowOverfunding'));
    }.property('isStatusCampaign', 'deadline', 'amount_needed', 'allowOverfunding'),

    isCheetahProject: Em.computed.equal('partner.id', 'cheetah'),

    save: function () {
        // the amount_needed is calculated here and not in the server
        this.set('amount_needed', this.get('calculatedAmountNeeded'));
        
        this._super();
    },

    isCheetahFunded: function(){
        // The project is funded for more than 30% but is not funded for the full 100%
        return (this.get('amount_donated') >= 0.3 * this.get('amount_asked') && !(this.get('amount_donated') >= this.get('amount_asked') ));
    }.property('amount_asked', 'amount_donated'),

    cheetahAmount: function() {
        return .7 * this.get('amount_asked')
    }.property('amount_asked')
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

    validBudgetBreakdown: function(){
        var lines = this.get('budgetLines')
        var result = false
        if (lines.content.length > 0){
            result = true;
        }
        return result;
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
    requiredGoalFields: ['amount_asked', 'deadline', 'maxAmountAsked', 'minAmountAsked', 'validBudgetBreakdown'],
    requiredPitchFields: ['validTitle', 'pitch', 'image', 'theme', 'tags.length', 'country', 'latitude', 'longitude'],

    friendlyFieldNames: {
        'validTitle': gettext('Title'),
        'title' : gettext('Title'),
        'pitch': gettext('Description'),
        'storyChanged' : gettext('Personalised story'),
        'image' : gettext('Image'),
        'theme' : gettext('Theme'),
        'tags.length': gettext('Tags'),
        'deadline' : gettext('Deadline'),
        'country' : gettext('Country'),
        'description': gettext('Why, what and how'),
        'goal' : gettext('Goal'),
        'destination_impact' : gettext('Destination impact'),
        'minAmountAsked' : gettext('Minimal amount asked'),
        'amount_asked': gettext('Amount asked'),
        'validBudgetBreakdown': gettext("Valid budget breakdown"),
        'story': gettext('Story')
    }

});



