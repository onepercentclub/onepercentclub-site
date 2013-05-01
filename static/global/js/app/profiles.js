/*
 Models
 */

/* User / Member authentication. */
App.Member = DS.Model.extend({
    url: 'members/users',

    username: DS.attr('string'),
    first_name: DS.attr('string'),
    last_name: DS.attr('string'),

    about: DS.attr('string'),
    why: DS.attr('string'),
    contribution: DS.attr('string'),
    availability: DS.attr('string'),
    working_location: DS.attr('string'),

    picture: DS.attr('string'),
    avatar: DS.attr('string'),

    getPicture: function(){
        if (this.get('picture')) {
            return this.get('picture')
        }
        return '/static/assets/images/default-avatar.png'
    }.property('avatar'),

    getAvatar: function(){
        if (this.get('avatar')) {
            return this.get('avatar')
        }
        return '/static/assets/images/default-avatar.png'
    }.property('avatar'),


    full_name: function() {
        return this.get('first_name') + ' ' + this.get('last_name');
    }.property('first_name', 'last_name'),

});

// Just like Member but without complete info
App.MemberPreview = App.Member.extend({
    url: 'members/users'
});


App.User = App.Member.extend({
    url: 'members',
    email: DS.attr('string')
});


/*
 Controllers
 */

// Inspiration from:
// http://stackoverflow.com/questions/14388249/accessing-controllers-from-other-controllers
App.CurrentUserController = Em.ObjectController.extend({
    init: function() {
        this._super();
        this.set("model", App.User.find('current'));
    },

    isAuthenticated: function(){
        return (this.get('username')) ? true : false;
    }.property('username')
});


App.MemberProfileController = Em.ObjectController.extend({
    loadProfile: function(){
        var model = this.get('model');

        //this.set('model', App.Member.find(model.get('id')));
    }.observes('model')
});

/*
 Views
 */


App.MemberProfileView = Em.View.extend({
    templateName: 'member_profile',
    classNames: ['member-profile']
});

