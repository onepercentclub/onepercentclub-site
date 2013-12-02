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
    video_url: DS.attr('string', {defaultValue: ''}),
    video_html: DS.attr('string'),

    amount: DS.attr('number'),
    amount_donated: DS.attr('number'),
    deadline: DS.attr('date'),

    amount_needed: function() {
        var donated = this.get('amount') - this.get('amount_donated');
        if(donated < 0) {
            return 0;
        }
        return Math.ceil(donated);
    }.property('amount', 'amount_donated'),

    is_funded: function() {
        return this.get('amount_needed') <= 0;
    }.property('amount_needed'),

    daysToGo: function(){
        var now = new Date();
        var microseconds = this.get('deadline').getTime() - now.getTime();
        return Math.ceil(microseconds / (1000 * 60 * 60 * 24));
    }.property('deadline')
});
