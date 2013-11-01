App.UserPreview = DS.Model.extend({
    url: undefined,

    username: DS.attr('string'),
    first_name: DS.attr('string'),
    last_name: DS.attr('string'),
    avatar: DS.attr('string'),

    full_name: function() {
        if (!this.get('first_name') && !this.get('last_name')) {
            return this.get('username');
        }
        return this.get('first_name') + ' ' + this.get('last_name');
    }.property('first_name', 'last_name'),

    getAvatar: function() {
        if (this.get('avatar')) {
            return this.get('avatar')
        }
        return STATIC_URL + 'images/default-avatar.png'
    }.property('avatar')

});

App.CurrentUser = App.UserPreview.extend({
    url: 'users',
    getUser: function(){
        return App.User.find(this.get('id_for_ember'));
    }.property('id_for_ember'),
    primary_language: DS.attr('string'),

    isAuthenticated: function(){
        return (this.get('username')) ? true : false;
    }.property('username'),

    id_for_ember: DS.attr('number')
});

App.Skill = DS.Model.extend({
    url: 'tasks/skills',
    name: DS.attr('string')
});

App.Theme = DS.Model.extend({
    url:'projects/themes',
    title: DS.attr('string')
});