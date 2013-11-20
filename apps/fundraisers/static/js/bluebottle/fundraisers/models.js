App.Adapter.map('App.FundRaiser', {
    owner: {embedded: 'load'}
});

App.FundRaiser = DS.Model.extend({
	url: 'fundraisers',

	project: DS.belongsTo('App.ProjectPreview'),
    owner: DS.belongsTo('App.UserPreview'),

	title: DS.attr('string'),
	description: DS.attr('string'),

	// Media
    image: DS.attr('image'),
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
    }.property('amount_donated', 'amount'),

    daysToGo: function(){
        var now = new Date();
        var microseconds = this.get('deadline').getTime() - now.getTime();
        return Math.ceil(microseconds / (1000 * 60 * 60 * 24));
    }.property('deadline')
});
