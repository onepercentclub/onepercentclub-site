App.Adapter.map('App.FundRaiser', {
    owner: {embedded: 'load'},
    project: {embedded: 'load'}
});

App.FundRaiser = DS.Model.extend({
	url: 'fundraiser/fundraisers',

	project: DS.belongsTo('App.ProjectPreview'), // TODO
    owner: DS.belongsTo('App.UserPreview'),

	title: DS.attr('string'),
	description: DS.attr('string'),

	// Media
    image: DS.attr('string'),
    image_small: DS.attr('string'),
    image_square: DS.attr('string'),
    image_bg: DS.attr('string'),

    video_url: DS.attr('string'),
    // video_html: DS.attr('string'),

    amount: DS.attr('number'),
    amount_donated: DS.attr('number'),
    deadline: DS.attr('date'),

    popover_title: function(){ // FIXME this should go in a view...
        return this.get('owner').get('full_name') + '\n' + this.get('title');
    }.property('owner', 'title'),

    popover_content: function(){ // FIXME this should go in a view...
        return this.get('amount_donated') + ' / ' + this.get('amount');
    }.property('amount_donated', 'amount')
});
