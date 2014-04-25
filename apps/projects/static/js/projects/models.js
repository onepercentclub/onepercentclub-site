App.Adapter.map('App.MyProject', {
    tags: {embedded: 'load'},
    budgetLines: {embedded: 'load'}
});

App.Project.reopen({

    deadline: DS.attr('date'),
    amount_asked: DS.attr('number', {defaultValue: 0}),

    maxAmountAsked: Ember.computed.lte('amount_asked', 1000000),
    minAmountAsked: Ember.computed.gte('amount_asked', 250),

    amount_donated: DS.attr('number', {defaultValue: 0}),
	amount_needed: DS.attr('number', {defaultValue: 0}),

	calculatedAmountNeeded: function() {
		    return this.get('amount_asked') - this.get('amount_donated');
    }.property('amount_asked', 'amount_donated'),

	task_count: DS.attr('number'),

    isFundable: Em.computed.equal('status.id', '5'),

    isStatusCampaign: Em.computed.equal('status.id', '5'),
    isStatusCompleted: Em.computed.equal('status.id', '7'),

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

    budgetTotal: function(){
        var lines = this.get('budgetLines');
        return lines.reduce(function(prev, line){
            return (prev || 0) + (line.get('amount')/1 || 0);
        });
    }.property('budgetLines.@each.amount'),

    init: function () {
        this._super();

        this.validatedFieldsProperty('validGoal', this.get('requiredGoalFields'));
        this.missingFieldsProperty('missingFieldsGoal', this.get('requiredGoalFields'));
    },

    valid: function(){
        return (this.get('') && this.get('validPitch') && this.get('validGoal') && this.get('organization.validOrganization')
			&& this.get('organization.validBank'));
    }.property('validStory', 'validPitch', 'validGoal', 'organization'),

    requiredStoryFields: ['story'],
    requiredGoalFields: ['amount_asked', 'deadline', 'maxAmountAsked', 'minAmountAsked'],
    requiredPitchFields: ['title', 'pitch', 'image', 'theme', 'tags.length', 'country', 'latitude', 'longitude'],

    friendlyFieldNames: {
        'title' : 'Title',
        'pitch': 'Description',
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
