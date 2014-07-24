App.Adapter.map('App.Partner', {
    projects: {embedded: 'load'}
});


App.Partner = DS.Model.extend({
    url: 'partners',
    name: DS.attr('string'),
    projects: DS.hasMany('App.ProjectPreview'),
    description: DS.attr('string'),
    image: DS.attr('image')
});
