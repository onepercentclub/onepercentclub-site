App.User = DS.Model.extend({
    url: 'users/profiles',

    username: DS.attr('string'),
    first_name: DS.attr('string'),
    last_name: DS.attr('string'),
    about: DS.attr('string'),
    why: DS.attr('string'),
    availability: DS.attr('string'),
    location: DS.attr('string'),

    picture: DS.attr('image'),

    website: DS.attr('string'),
    date_joined: DS.attr('date'),
    file: DS.attr('string'),

    // post-only fields (i.e. only used for user creation)
    email: DS.attr('string'),
    password: DS.attr('string'),

    getPicture: function() {
        if (this.get('picture')) {
            return MEDIA_URL + this.get('picture.large')
        }
        return STATIC_URL + 'images/default-avatar.png'
    }.property('picture'),

    getAvatar: function(){
        if (this.get('picture')) {
            return this.get('picture.square')
        }
        return STATIC_URL + 'images/default-avatar.png'
    }.property('picture'),

    full_name: function() {
        if (!this.get('first_name') && !this.get('last_name')) {
            return this.get('username');
        }
        return this.get('first_name') + ' ' + this.get('last_name');
    }.property('first_name', 'last_name'),

    user_since: function() {
        return Globalize.format(this.get('date_joined'), 'd');
    }.property('date_joined')
});

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