$(function() {
require(['libs/humanize']);

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
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
        initBehaviour(this.$);
        this._super();
    },
    
    templateForName: function(name, type) {
        if (!name) {
            return "";
        }
        var templates = Em.get(this, 'templates'),
            template = Em.get(templates, name),
            view = this;
        if (template) {
            return template;
        } else {
            view.set('templateName', 'waiting');
            require(['app/data_source'], function(){
                // Check if a templateFile is specified otherwise use templateName (name)
                var file = view.get('templateFile') ? view.get('templateFile') : name; 
                App.dataSource.getTemplate(file, function(data) {
                    // Iterate through handlebar tags
                    $(data).filter('script[type="text/x-handlebars"]').each(function() {
                        // Only load the template we're looking for
                        if (name == $(this).attr('data-template-name')) {
                            var raw = $(this).html();
                            var template = Em.Handlebars.compile(raw);
                            Em.TEMPLATES[name] = template;
                            view.set('templateName', name);
                            view.rerender();
                        }
                    });
                });
            });
        }
    }
});

App = Em.Application.create({
    rootElement : '#content',
    
    // Define the main application controller. This is automatically picked up by
    // the application and initialized.
    ApplicationController : Em.Controller.extend({
    }),

    ApplicationView : Em.View.extend({
        templateName : 'application'
    }),

    // Use this to clear an outlet
    EmptyView : Em.View.extend({
        template : ''
    }),

    /* Home */
    HomeView : Em.View.extend({
        templateName : 'home'
    })

});

App.store =  DS.Store.create({
  revision: 7,
  adapter: DS.DRF2Adapter.create()
});

/* Base Controllers */

// Controller to get lists from API
App.ListController = Em.ArrayController.extend({
    filterParams: {},
    getList: function(filterParams){
        this.set("content", App.store.find(this.get('model')));
    }
    
});

// Controller to get single records from API
App.DetailController = Em.ObjectController.extend({
    filterParams: {},
    getPkValue: function(){
        var params = this.get('filterParams');
        pk = "";
        if (undefined !== params['slug']) {
            pk = params['slug'];
        } else if (undefined !== params['id']) {
            pk = params['id'];
        } else if (undefined !== params['pk']) {
            pk = params['pk'];
        }
        return pk;
    }, 

    getDetail: function(filterParams){
        if (filterParams) {
            this.set('filterParams', filterParams);
        }
        this.set("content", App.store.find(this.get('model'), this.getPkValue()));
    }
});

App.FormController = Em.ObjectController.extend({
    filterParams: {}
});

App.Member = DS.Model.extend({
    url: 'members/users',
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


App.userController = App.DetailController.create({
    model: App.User,
    init: function(){
        this._super();
        this.getCurrent();
    },
    getCurrent: function(filterParams){
        var user = App.store.find(this.get('model'), 'current');
        this.set("content", user);
    }
})


/* Routing */

// Set wallpost route
App.WallpostsRoute = Em.Route.extend({
    route: '/wallposts',

    showWallpostForm: Em.Route.transitionTo('wallposts.form'),
    

    start: Em.Route.extend({
        route: "/"
    }),
    
    form: Em.Route.extend({
        route: '/form',
        connectOutlets: function(router, context) {
            require(['app/wallposts'], function(){
                router.get('applicationController').connectOutlet('topPanel', 'wallpostForm');
                router.get('applicationController').connectOutlet('midPanel', 'empty');
                router.get('applicationController').connectOutlet('bottomPanel', 'empty');
            });
        }
    }) 
});


// Set blogs route
App.BlogsRoute = Em.Route.extend({
    route: '/blogs',

    showBlogDetail: Em.Route.transitionTo('blogs.detail'),

    connectOutlets : function(router, context) {
        require(['app/blogs'], function(){
            App.blogListController.getList();
            router.get('applicationController').connectOutlet('topPanel', 'blogList');
            router.get('applicationController').connectOutlet('midPanel', 'empty');
            router.get('applicationController').connectOutlet('bottomPanel', 'empty');
        });
    },

    start: Em.Route.extend({
        route: "/"
    }),

    detail: Em.Route.extend({
        route: '/:slug',
        deserialize: function(router, context) {
            // TODO: See if we can stick to just  context.get('slug')
            // Now the Ember action and the 'bookmarked' page need \
            // different approach
            var slug = context.slug ? context.slug : context.get('slug');
            return {slug: slug}
        },
        serialize: function(router, context) {
            // TODO: See if we can stick to just  context.get('slug')
            var slug = context.slug ? context.slug : context.get('slug');
            return {slug: slug};
        },
        connectOutlets: function(router, context) {
            require(['app/blogs', 'app/reactions'], function(){
                // TODO: See if we can stick to just  context.get('slug')
                var slug = context.slug ? context.slug : context.get('slug');
                App.blogDetailController.getDetail({'slug': slug});
                // TODO: use the detail from the line above to pass to call below
                App.reactionListController.getList({'type': 'blogs', 'slug': slug});
                router.get('applicationController').connectOutlet('topPanel', 'blogHeader');
                router.get('applicationController').connectOutlet('midPanel', 'blogDetail');
                router.get('applicationController').connectOutlet('bottomPanel', 'reactionBox');
                router.get('applicationController').connectOutlet('reactionForm', 'reactionForm');
                router.get('applicationController').connectOutlet('reactionList', 'reactionList');
            });
        } 
    }) 
});

// Set basic Project route
App.ProjectsRoute = Em.Route.extend({
    route: '/projects',

    showProjectDetail: Em.Route.transitionTo('projects.detail'),
    

    connectOutlets : function(router, context) {
        require(['app/projects'], function(){
            router.get('applicationController').connectOutlet('topPanel', 'projectStart');
            router.get('applicationController').connectOutlet('midPanel', 'projectSearchForm');
            router.get('applicationController').connectOutlet('bottomPanel', 'projectSearchResultsSection');
        });
    },

    // The project start state.
    start: Em.Route.extend({
        route: "/"
    }),

    // The project detail state.
    detail: Em.Route.extend({
        route: '/:project_slug',
        deserialize: function(router, params) {
            return {slug: params.project_slug}
        },
        serialize: function(router, context) {
            return {project_slug: context.slug};                router.get('applicationController').connectOutlet('midPanel', 'empty');
                router.get('applicationController').connectOutlet('bottomPanel', 'empty');

        },
        connectOutlets: function(router, context) {
            require(['app/projects'], function(){
                App.projectDetailController.populate(context.slug);
                router.get('applicationController').connectOutlet('topPanel', 'projectDetail');
                router.get('applicationController').connectOutlet('midPanel', 'empty');
                router.get('applicationController').connectOutlet('bottomPanel', 'empty');
            });
        }
    }) 
});



App.RootRoute = Em.Route.extend({
    // Used for navigation
    showHome: Em.Route.transitionTo('home'),
    showProjectStart: Em.Route.transitionTo('projects.start'),
    showBlogStart: Em.Route.transitionTo('blogs.start'),

    // The actual routing
    home: Em.Route.extend({
        route : '/',
        connectOutlets: function(router, context) {
            router.get('applicationController').connectOutlet('topPanel', 'home');
            router.get('applicationController').connectOutlet('midPanel', 'empty');
            router.get('applicationController').connectOutlet('bottomPanel', 'empty');
        }
    }),
    wallposts: App.WallpostsRoute,
    projects: App.ProjectsRoute,
    blogs: App.BlogsRoute
});

App.Router = Em.Router.extend({
    location: 'hash',
    root: App.RootRoute
});



});
