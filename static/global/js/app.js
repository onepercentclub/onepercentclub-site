App = Em.Application.create({
    rootElement : '#content',
    
    // Define the main application controller. This is automatically picked up by
    // the application and initialized.
    ApplicationController : Em.Controller.extend({
        // TODO: Is there a better way of doing this?
        currentMenu: function(){
            var currentState  = this.get('target.location.lastSetURL');
            var menu = currentState.split("/");
            currentState = menu[1]||'home';
            
            return currentState;
        }.property('target.location.lastSetURL')
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


/**
 * Reopen Ember View to add on-the-fly loading of templates
 * 
 */
Em.View.reopen({
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
                App.dataSource.getTemplate(name, function(data) {
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

/* Routing */

// Set basic Project route
App.ProjectRoute = Em.Route.extend({
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
            return {project_slug: context.slug};
        },
        connectOutlets: function(router, context) {
            require(['app/projects'], function(){
                App.projectDetailController.populate(context.slug);
                router.get('applicationController').connectOutlet('topPanel', 'projectDetail');
            });
        }
    }) 
});


// Set basic Project route
App.SupportRoute = Em.Route.extend({
    route: '/support',

    connectOutlets : function(router, context) {
        require(['app/support'], function(){
            router.get('applicationController').connectOutlet('topPanel', 'supportSelect');
            router.get('applicationController').connectOutlet('midPanel', 'empty');
            router.get('applicationController').connectOutlet('bottomPanel', 'empty');
        });
    },

    // The project start state.
    start: Em.Route.extend({
        route: "/"
    }),

});


App.RootRoute = Em.Route.extend({
    // Used for navigation
    showHome: Em.Route.transitionTo('home'),

    showProjectStart: Em.Route.transitionTo('projects.start'),

    // The actual routing
    home: Em.Route.extend({
        route : '/',
        connectOutlets: function(router, context) {
            router.get('applicationController').connectOutlet('topPanel', 'home');
            router.get('applicationController').connectOutlet('midPanel', 'empty');
            router.get('applicationController').connectOutlet('bottomPanel', 'empty');
        }
    }),
    projects: App.ProjectRoute,
    support: App.SupportRoute,
});

App.Router = Em.Router.extend({
    location: 'hash',
    root: App.RootRoute
});

$(function() {
    App.initialize();
});

