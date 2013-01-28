
/*
 Models
 */

App.Country = DS.Model.extend({
    name: DS.attr('string'),
    subregion: DS.attr('string')
});


App.Project = DS.Model.extend({
    url: 'projects',

    // Model fields
    slug: DS.attr('string'),
    title: DS.attr('string'),
    image: DS.attr('string'),
    phase: DS.attr('string'),
    organization: DS.attr('string'),
    description: DS.attr('string'),
    money_asked: DS.attr('number'),
    money_donated: DS.attr('number'),
    tags: DS.attr('array'),
    owner: DS.belongsTo('App.Member'),
    country: DS.belongsTo('App.Country'),

    // FIXME: For now we set some default values here because we don't have actual numbers
    supporter_count: DS.attr('number', {defaultValue: 123}),
    days_left: DS.attr('number', {defaultValue: 123})

// TODO: defaultValue doesn't seem to be working with Ember 1.0.0 pre4
//    // FIXME: For now we do some html generating here.
//    // TODO: solve this in Ember or Handlebars helper
//    days_left_span: function() {
//        var dl = this.get('days_left').toString();
//        var html = '';
//        for (var i = 0, len = dl.length; i < len; i += 1) {
//            html += '<span>' + dl.charAt(i) + '</span>'
//        }
//        return html;
//    }.property('days_left'),
//
//    supporter_count_span: function() {
//        var dl = this.get('supporter_count').toString();
//        var html = '';
//        for (var i = 0, len = dl.length; i < len; i += 1) {
//            html += '<span>' + dl.charAt(i) + '</span>'
//        }
//        return html;
//    }.property('supporter_count')
});


/*
 Views
 */

App.ProjectSupportersView = Em.View.extend({
    templateName: 'project_supporters'
});


App.ProjectListView = Em.View.extend({
    templateName: 'project_list'
});