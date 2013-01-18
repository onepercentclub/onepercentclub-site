//$(function() {

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrf_token = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function sameOrigin(url) {
        // If url starts with / it's relative and same origin
        if (url.substr(0, 1) == '/') {
            return true;
        }
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/');
        // or any other URL that isn't scheme relative or absolute i.e relative. !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    Em.Controller.reopen({
        userBinding: "App.userController.content"
    });

    Em.View.reopen({
        userBinding: "App.userController.content",
        isLoggedInBinding: "App.userController.isLoggedIn",
//        didInsertElement: function() {
//            // Re-init all behaviours defined in main.js
//            // TODO: Move all behaviour to Ember app?
//            try {
//                initBehaviour(this.get('$'));
//            } catch (err) {
//                // Some views cough on this...
//                // TODO: Find out which views (the first?) causes problems and why
//            }
//            this._super();
//        },

    });

    App = Em.Application.create({
        _getTemplate: function(template, callback) {
            var hash = {};
            hash.url = '/en/templates/' + template + '.hbs';
            hash.type = 'GET';
//            hash.dataType = 'html';
            hash.contentType = 'application/json';
            hash.success = callback;
            hash.error = function(jqXHR, textStatus, errorThrown) {
                throw errorThrown + ' ' + hash.url;
            };
            jQuery.ajax(hash);
        },

        loadTemplate: function(templateFilename) {
//            if (!templateName || Em.TEMPLATES[templateName]) {
//                return;
//            }
            this._getTemplate(templateFilename, function(data) {
                // Iterate through handlebar tags
                $(data).filter('script[type="text/x-handlebars"]').each(function() {
                    var templateName = $(this).attr('data-template-name');
                    var raw = $(this).html();
                    Em.TEMPLATES[templateName] = Em.Handlebars.compile(raw);
                });
            });
        },

        loadTemplates: function(templateFilenames) {
            var app = this;
            templateFilenames.forEach(function (templateFilename) {
                app.loadTemplate(templateFilename);
            });
        }

    });

// The Ember Data Adapter and Store configuration.

    App.Adapter = DS.DRF2Adapter.extend({
        namespace: "i18n/api",

        plurals: {
            "projects/wallposts/media": "projects/wallposts/media",
            "projects/wallposts/text": "projects/wallposts/text"
        }

    });

// Embedded Model Mapping
//
// http://stackoverflow.com/questions/14320925/how-to-make-embedded-hasmany-relationships-work-with-ember-data/14324532#14324532
// The two possible values of embedded are:
//   load: The child records are embedded when loading, but should be saved as standalone records. In order
//         for this to work, the child records must have an ID.
//   always: The child records are embedded when loading, and are saved embedded in the same record. This,
//           of course, affects the dirtiness of the records (if the child record changes, the adapter will
//           mark the parent record as dirty).
    App.Adapter.map('App.Project', {
        owner: {embedded: 'load'},
        country: {embedded: 'load'}
    });
    App.Adapter.map('App.Projectwallpost', {
        author: {embedded: 'load'},
        photos: {embedded: 'load'},
        reactions: {embedded: 'load'}
    });

    App.store = DS.Store.create({
        revision: 11,

        adapter: App.Adapter.create()
    });


    App.Member = DS.Model.extend({
        url: 'members/users',

        username: DS.attr('string'),
        first_name: DS.attr('string'),
        last_name: DS.attr('string'),
        picture: DS.attr('string'),

        full_name: function() {
            return this.get('first_name') + ' ' + this.get('last_name');
        }.property('first_name', 'last_name')
    });


    App.User = App.Member.extend({
        url: 'members',

        is_authenticated: function(){
            return (this.get('username'))  ? true : false;
        }.property('username')
    });

// TODO: This needs to be changed to extend(). See note about this here:
// https://github.com/emberjs/ember.js/commit/c1c720781c976f69fd4014ea50a1fee652286048
    App.userController = Em.ObjectController.createWithMixins({
        init: function() {
            this._super();
            this.getCurrent();
        },
        getCurrent: function(filterParams) {
            this.set("content", App.User.find('current'));
        }
    });


    /* Routing */

//    Ember.Route.reopen({
//        renderTemplate: function(controller, model) {
//            this.render();
//
//
//        }
//    });

    App.SlugRouter = Em.Mixin.create({
        serialize: function(model, params) {
            if (params.length !== 1) { return {}; }

            var name = params[0], object = {};
            object[name] = get(model, 'slug');

            return object;
        }
    });


    App.Router.map(function() {
        this.route("home", { path: "/" });
        this.resource('projects', {path: '/projects'}, function() {
            this.route('new');
            this.route('search');
        });
        this.resource('project', {path: '/projects/:slug'}, function() {
            this.route('edit');
            this.resource('projectwallpost', {path: '/wallposts/:projectwallpost_id'});
        });
    });


    App.ProjectsRoute = Ember.Route.extend({
        model: function() {
            return App.Project.find({phase: 'fund'});
        }
    });


    App.ProjectRoute = Ember.Route.extend(App.SlugRouter, {
        model: function(params) {
            return App.Project.find(params.slug);
        },

        setupController: function(controller, project) {
            // Project detail controller.
            controller.set('content', project);

            // Wallposts list controller.
            var wallpostsController = this.controllerFor('projectwallposts');
            // The RecordArray returned by findQuery can't be manipulated directly so we're converting it to an Ember array.
            // http://stackoverflow.com/questions/11895629/add-delete-items-from-ember-data-backed-arraycontroller
            // https://github.com/emberjs/data/issues/370
            wallpostsController.set('content', App.Projectwallpost.find({project_slug: project.get('slug')}).toArray());

            // WallPost creation form controller.
            var newWallpostController = this.controllerFor('projectwallpostNew');
            newWallpostController.set('currentProject', project);
            newWallpostController.set('projectwallpostsController', wallpostsController);
        },

        renderTemplate: function(controller, model) {
            this._super();

            // Render the wallposts list.
            this.render('projectwallposts', {
                into: 'project',
                outlet: 'projectwallposts',
                controller: 'projectwallposts'
            });

            // Render the wallpost creation form.
            this.render('wallpost_new', {
                into: 'project',
                outlet: 'wallpostnew',
                controller: 'projectwallpostNew'
            });
        }
    });

    App.ProjectwallpostRoute = Ember.Route.extend({
        model: function(params) {
            return App.Projectwallpost.find(params.projectwallpost_id);
        },
        setupController: function(controller, wallpost) {
            console.log(this.toString() + '.setupController');
            controller.set('content', wallpost);
        }
    });

//});
