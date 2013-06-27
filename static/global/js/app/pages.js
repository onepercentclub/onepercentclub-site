/* Models */

App.Page = DS.Model.extend({
    url: 'pages',
    title: DS.attr('string'),
    body: DS.attr('string')
});

