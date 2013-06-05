/*
 Models
 */

/*
  A data model representing a user.

  Interacts with following public API:

  User Detail (GET/PUT):   /users/profiles/<pk>
 */
App.User = DS.Model.extend({
    url: 'users/profiles',

    username: DS.attr('string'),
    first_name: DS.attr('string'),
    last_name: DS.attr('string'),
    about: DS.attr('string'),
    why: DS.attr('string'),
    availability: DS.attr('string'),
    location: DS.attr('string'),
    picture: DS.attr('string'),
    avatar: DS.attr('string'),
    website: DS.attr('string'),
    date_joined: DS.attr('date'),

    // post-only fields (i.e. only used for user creation)
    email: DS.attr('string'),
    password: DS.attr('string'),

    getPicture: function() {
        if (this.get('picture')) {
            return this.get('picture')
        }
        return '/static/assets/images/default-avatar.png'
    }.property('picture'),

    getAvatar: function(){
        if (this.get('avatar')) {
            return this.get('avatar')
        }
        return '/static/assets/images/default-avatar.png'
    }.property('avatar'),

    full_name: function() {
        if (!this.get('first_name') && !this.get('last_name')) {
            return this.get('username');
        }
        return this.get('first_name') + ' ' + this.get('last_name');
    }.property('first_name', 'last_name'),

    user_since: function() {
        return Globalize.format(this.get('date_joined'), 'd');
    }.property('date_joined'),

    didUpdate: function() {
        alert('Your profile info is updated.');
    }
});

/*
 A data model representing a user's settings.

 Interacts with following authenticated user API.

 User settings Detail (GET/PUT):  /users/settings/<pk>
 */
App.UserSettings = DS.Model.extend({
    url: 'users/settings',

    email: DS.attr('string'),
    newsletter: DS.attr('boolean'),
    share_time_knowledge: DS.attr('boolean'),
    share_money: DS.attr('boolean'),
    gender: DS.attr('string'),
    birthdate: DS.attr('date'),

    didUpdate: function() {
        alert('Your account settings is updated.');
    }
});

App.UserPreview = DS.Model.extend({
    // There is no url for UserPreview because it's embedded.
    url: undefined,

    username: DS.attr('string'),
    first_name: DS.attr('string'),
    last_name: DS.attr('string'),
    avatar: DS.attr('string'),

    getAvatar: function() {
        if (this.get('avatar')) {
            return this.get('avatar')
        }
        return '/static/assets/images/default-avatar.png'
    }.property('avatar')
});

/*
 A data model representing currently authenticated user.

 Interacts with following authenticated user API.
 Logged in user (GET):            /users/current

 TODO: Should be unified to App.User model.
 */
App.CurrentUser = App.UserPreview.extend({
    url: 'users',

    // This is a hack to work around an issue with Ember-Data keeping the id as 'current'.
    // App.UserSettingsModel.find(App.CurrentUser.find('current').get('id_for_ember'));
    id_for_ember: DS.attr('number')
});

/*
 Controllers
 */

// Inspiration from:
// http://stackoverflow.com/questions/14388249/accessing-controllers-from-other-controllers
App.CurrentUserController = Em.ObjectController.extend({
    init: function() {
        this._super();
        this.set("model", App.CurrentUser.find('current'));
    },

    isAuthenticated: function(){
        return (this.get('username')) ? true : false;
    }.property('username')
});


App.UserController = Ember.Controller.extend({
    needs: "currentUser"
});


App.UserProfileController = Ember.ObjectController.extend(App.Editable, {
    timeAvailableList: (function() {
        var list = Em.A();
        list.addObject({ name: '- - - - - - - - - - - - - - - - - -', value: ''});
        list.addObject({ name: '1-4 hours per week', value: '1-4_hours_week' });
        list.addObject({ name: '5-8 hours per week', value: '5-8_hours_week' });
        list.addObject({ name: '9-16 hours per week', value: '9-16_hours_week' });
        list.addObject({ name: '1-4 hours per month', value: '1-4_hours_month' });
        list.addObject({ name: '5-8 hours per month', value: '5-8_hours_month' });
        list.addObject({ name: '9-16 hours per month', value: '9-16_hours_month' });
        list.addObject({ name: 'I have all the time in the world. Bring it on :D', value: 'lots_of_time' });
        list.addObject({ name: 'It depends on the content of the tasks. Challenge me!', value: 'depends' });
        return list;
    }).property(),

    addFile: function(file) {
        this.set('model.file', file);
    },

    save: function(profile) {
        profile.get('transaction').commit();
    }
});


App.UserSettingsController = Ember.ObjectController.extend(App.Editable, {
    save: function(settings) {
        settings.get('transaction').commit();
    }
});


App.UserModalController = Ember.ObjectController.extend({
    loadProfile: function() {
        var model = this.get('model');
        this.set('model', App.User.find(model.get('id')));
    }.observes('model')
});


App.SignupController = Ember.ObjectController.extend({
    needs: "currentUser",

    createUser: function(user) {
        var self = this;

        user.on('didCreate', function() {
            var data = {
                // The key for the login needs to be 'username' for logins to work.
                'username': self.get('email'),
                'password': self.get('password'),
                'csrfmiddlewaretoken': csrf_token
            };

            /*
             Log the user automatically in after successful signup.
             */
            $.ajax({
                type: "POST",
                url: "/accounts/login/",
                data: data,
                success: function() {
                    // TODO: Personalize the home page so the user becomes
                    //       aware that he is successfully logged in.
                    // self.replaceRoute('home');
                    window.location.replace('/');
                }
            });
        });

        user.set('url', 'users');  // Change the model URL to the User creation API.
        user.get('transaction').commit();
    }
});


App.UserModalView = Em.View.extend({
    templateName: 'user_modal'
});
