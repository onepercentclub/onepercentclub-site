App.FundRaiser = DS.Model.extend({
	url: 'fundraiser/fundraisers',

	project: DS.belongsTo('App.ProjectPreview'), // TODO

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
    deadline: DS.attr('date')
});