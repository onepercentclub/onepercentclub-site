App.Campaign = DS.Model.extend({
	title: DS.attr('string'),
    start: DS.attr('date'),
    end: DS.attr('date'),

	target: DS.attr('number'),
	amount_donated: DS.attr('number'),
});