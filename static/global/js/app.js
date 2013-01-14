$(function() {
    require(['libs/humanize']);


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
        if (url.substr(0,1) == '/') {
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
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/')
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

    Em.View.reopen({
        userBinding: "App.userController.content",
        isLoggedInBinding: "App.userController.isLoggedIn",
        didInsertElement: function() {
            // Re-init all behaviours defined in main.js
            // TODO: Move all behaviour to Ember app?
            try {
                initBehaviour(this.get('$'));
            } catch (err) {
                // Some views cough on this...
                // TODO: Find out which views (the first?) causes problems and why
            }
            this._super();
        },


        getTemplate: function(template, callback) {
            var hash = {};
            // TODO: Move templates URL to a language independent location.
            hash.url = '/en/templates/' + template + '.hb.html';
            hash.type = 'GET';
            hash.dataType = 'html';
            hash.contentType = 'application/json';
            hash.success = callback;
            hash.error = function(jqXHR, textStatus, errorThrown) {
                throw errorThrown + ' ' + hash.url;
            };
            jQuery.ajax(hash);
        },


        templateForName: function(templateName, type) {
            if (!templateName) {
                return "";
            }
            if (Em.TEMPLATES[templateName]) {
                return Em.TEMPLATES[templateName];
            } else {
                this.set('templateName', 'waiting');
                // Check if a templateFile is specified otherwise use templateName as the template filename.
                var templateFile = this.get('templateFile') ? this.get('templateFile') : templateName;
                var view = this;
                this.getTemplate(templateFile, function(data) {
                    // Iterate through handlebar tags
                    $(data).filter('script[type="text/x-handlebars"]').each(function() {
                        var curTemplateName = $(this).attr('data-template-name');
                        var raw = $(this).html();
                        Em.TEMPLATES[curTemplateName] = Em.Handlebars.compile(raw);
                        if (templateName == curTemplateName) {
                            view.set('templateName', templateName);
                            view.rerender();
                        }
                    });
                });
            }
        }
    });

    App = Em.Application.create({
        rootElement: '#content',

        // Define the main application controller. This is automatically picked up by the application and initialized.
        ApplicationController: Em.Controller.extend({
        }),

        ApplicationView: Em.View.extend({
            templateName: 'application'
        }),

        // Use this to clear an outlet
        EmptyView: Em.View.extend({
            template: ''
        }),

        /* Home */
        HomeView: Em.View.extend({
            templateName: 'home'
        })

    });

    App.store = DS.Store.create({
        revision: 7,
        adapter: DS.DRF2Adapter.create({
            namespace: "i18n/api"
        })
    });

    /* Base Controllers */

    // Controller to get lists from API
    App.ListController = Em.ArrayController.extend({
        filterParams: {},
        getList: function(filterParams) {
            if (undefined !== filterParams) {
                this.set('filterParams', filterParams);
            }
            this.set('content', App.store.find(this.get('model'), this.get('filterParams')));
        }
    });

    App.FormController = Em.ObjectController.extend({
        filterParams: {}
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
        url: 'members'
    });


    App.userController = Em.ObjectController.create({
        model: App.User,
        init: function() {
            this._super();
            this.getCurrent();
        },
        getCurrent: function(filterParams) {
            var user = App.store.find(this.get('model'), 'current');
            this.set("content", user);
        }
    });


    /* Routing */

    // Set blogs route
    App.BlogsRoute = Em.Route.extend({
        route: '/blogs',

        showBlogDetail: Em.Route.transitionTo('blogs.detail'),


        index: Em.Route.extend({
            route: '/',
            connectOutlets: function(router, context) {
                require(['app/blogs'], function() {
                    App.blogListController.getList();
                    router.get('applicationController').connectOutlet('topPanel', 'blogList');
                    router.get('applicationController').connectOutlet('midPanel', 'empty');
                    router.get('applicationController').connectOutlet('bottomPanel', 'empty');
                });
            }
        }),

        detail: Em.Route.extend({
            route: '/:slug',
            deserialize: function(router, params) {
                return {slug: Em.get(params, 'slug')}
            },
            serialize: function(router, blog) {
                return {slug: Em.get(blog, 'slug')};
            },
            connectOutlets: function(router, context) {
                require(['app/blogs', 'app/reactions'], function() {
                    // TODO: See if we can stick to just  context.get('slug')
                    var slug = context.slug ? context.slug : context.get('slug');
                    App.blogDetailController.getDetail({'slug': slug});
                    // TODO: use the detail from the line above to pass to call below
                    App.reactionListController.getList({'type': 'blogs', 'slug': slug});
                    router.get('applicationController').connectOutlet('topPanel', 'blogHeader');
                    router.get('applicationController').connectOutlet('midPanel', 'blogDetail');
                    router.get('applicationController').connectOutlet('bottomPanel', 'reactionBox');
                    router.get('applicationController').connectOutlet('reactionForm', 'reactionForm');
                    router.get('applicationController').connectOutlet('reactionActions', 'reactionActions');
                    router.get('applicationController').connectOutlet('reactionList', 'reactionList');
                });
            }
        })
    });

    // Set basic Project route
    App.ProjectsRoute = Em.Route.extend({
        route: '/projects',

        showProjectDetail: Em.Route.transitionTo('projects.detail'),

        // The project start state.
        index: Em.Route.extend({
            route: '/',
            connectOutlets: function(router, context) {
                require(['app/projects'], function() {
                    App.projectListController.set('content', App.Project.find({phase: 'fund'}));
                    router.get('applicationController').connectOutlet('topPanel', 'empty');
                    router.get('applicationController').connectOutlet('midPanel', 'projectList');
                    router.get('applicationController').connectOutlet('bottomPanel', 'empty');
                });
            }
        }),

        // The project detail state.
        detail: Em.Route.extend({
            route: '/:slug',
            deserialize: function(router, params) {
                return {slug: Em.get(params, 'slug')}
            },
            serialize: function(router, project) {
                return {slug: Em.get(project, 'slug')};
            },
            connectOutlets: function(router, project) {
                require(['app/projects', 'app/wallposts', 'app/reactions'], function() {
                    var id = Em.get(project, 'id'),
                        slug = Em.get(project, 'slug');
                    if (id) {
                        App.projectDetailController.set('content', App.Project.find(id));
                    } else if (slug) {
                        var projects = App.Project.find({slug: slug});
                        // observe the length of projects, so if the project is loaded (eg length 0 -> 1)
                        // we can update projectDetailController
                        // TODO: Every 5 refresh it returns a project detail page without project details
                        projects.addObserver('content', function(sender, key) {
                            // TODO implement 404 page:
                            // if (this.length < 1)
                            //     Em.Route.transitionTo('404');
                            App.projectDetailController.set('content', this.objectAt(0));
                        });
                    } else {
                        Em.assert("Project id and slug cannot be determined. Can't continue.", false);
                    }

                    router.get('applicationController').connectOutlet('topPanel', 'projectDetail');
                    router.get('applicationController').connectOutlet('midPanel', 'wallPostFormContainer');
                    router.get('applicationController').connectOutlet('bottomPanel', 'projectWallPostList');
                });
            }
        })
    });


    App.RootRoute = Em.Route.extend({
        // Used for navigation
        showHome: Em.Route.transitionTo('home'),
        showProjectStart: Em.Route.transitionTo('projects.index'),
        showBlogStart: Em.Route.transitionTo('blogs.index'),

        // The actual routing
        home: Em.Route.extend({
            route: '/',
            connectOutlets: function(router, context) {
                router.get('applicationController').connectOutlet('topPanel', 'home');
                router.get('applicationController').connectOutlet('midPanel', 'empty');
                router.get('applicationController').connectOutlet('bottomPanel', 'empty');
            }
        }),
        projects: App.ProjectsRoute,
        blogs: App.BlogsRoute
    });

    App.Router = Em.Router.extend({
        location: 'hash',
        root: App.RootRoute
    });

});
