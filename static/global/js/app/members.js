App.Member = DS.Model.extend({
    url: 'members',
    first_name: DS.attr('string'),
    last_name: DS.attr('string'),
    picture: DS.attr('string'),
    full_name: function() {
        return this.get('first_name') + ' ' + this.get('last_name');
    }.property('first_name', 'last_name')
});