App.Adapter.map('App.GroupPage', {
    owner: {embedded: 'load'},
    members: {embedded: 'load'},
    projects: {embedded: 'load'},
    slides: {embedded: 'load'}
});


App.GroupPageSlide = DS.Model.extend({
    title: DS.attr('string'),
    body: DS.attr('string'),
    image: DS.attr('string'),

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


App.GroupPage = DS.Model.extend({
    url: 'groups',

    title: DS.attr('string'),
    slides: DS.hasMany('App.GroupPageSlide'),
    projects: DS.hasMany('App.ProjectPreview'),
    members: DS.hasMany('App.UserPreview')
});
