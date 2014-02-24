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
