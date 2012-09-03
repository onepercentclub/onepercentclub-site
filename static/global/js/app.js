App = Em.Application.create({
    rootElement : '#content',

    updateRouter : function() {
        var router = this.get('router');
        router.init();
        console.log(router)
        console.log('Don\'t know how to update the router, yet....')
    },

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

/* Routing */

// Set basic Project route
App.ProjectRoute = Em.Route.extend({
    route : '/projects',
    projectDetail: function(router, event) {
        router.transitionTo('projects.detail', event.context);
    },
    connectOutlets : function(router, context) {
        require(['app/projects'], function(){
            router.get('applicationController').connectOutlet('topPanel', 'projectStart');
            router.get('applicationController').connectOutlet('midPanel', 'projectSearchForm');
            router.get('applicationController').connectOutlet('bottomPanel', 'projectSearchResultsSection');
        });
    },
    detail: Em.Route.extend({
        route: '/:project',
        changeMediaViewer: function(router, event){
            console.log(event);
        },
        deserialize: function(router, params) {
            return {slug: params.project}
        },
        serialize: function(router, context) {
            return {project: context.slug};
        },
        connectOutlets : function(router, context) {
            require(['app/projects'], function(){
                App.projectDetailController.populate(context.slug);
                router.get('applicationController').connectOutlet('topPanel', 'projectDetail');
            });
        }
    }) 
});

App.RootRoute = Em.Route.extend({
    // Used for navigation
    gotoHome : function(router, event) {
        router.transitionTo('home');
    },
    gotoProjectInfo : function(router, event) {
        router.transitionTo('projects.info');
    },
    gotoProjects : function(router, event) {
        router.transitionTo('projects');
    },
    // Language switching
    switchLanguage : function(router, event) {
        //TODO: implement language switch
        //TODO: Do class switch in a proper Ember way...
        $('a', '.languages').removeClass('active');
        $(event.srcElement).addClass('active');
    },
    // The actual routing
    home : Em.Route.extend({
        route : '/',
        connectOutlets: function(router, context) {
            router.get('applicationController').connectOutlet('topPanel', 'home');
            router.get('applicationController').connectOutlet('midPanel', 'empty');
            router.get('applicationController').connectOutlet('bottomPanel', 'empty');
        }
    }),
    projects: App.ProjectRoute
});

App.Router = Em.Router.extend({
    history: 'hash',
    root: App.RootRoute
});

$(function() {
    App.initialize();
});

