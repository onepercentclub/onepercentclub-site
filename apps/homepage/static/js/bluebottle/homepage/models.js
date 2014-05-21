App.Adapter.map('App.HomePage', {
    projects: {embedded: 'load'},
    slides: {embedded: 'load'},
    impact: {embedded: 'load'},
    quotes: {embedded: 'load'}
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
    impact: DS.belongsTo('App.Impact'),
    quotes: DS.hasMany('App.Quote')
});
