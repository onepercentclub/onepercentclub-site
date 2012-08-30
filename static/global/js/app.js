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
    }),

});

/* Routing */

// Set basic Project route
App.ProjectRoute = Em.Route.extend({
    route : '/projects',
    connectOutlets : function(router, event) {
        require(['app/projects'], function() {
            router.get('applicationController').connectOutlet('topPanel', 'projectHome');
            router.get('applicationController').connectOutlet('midPanel', 'projectSearchForm');
            router.get('applicationController').connectOutlet('bottomPanel', 'projectSearchResults');
        });
    },
    info : Em.Route.extend({
        route : '/info',
        connectOutlets : function(router, event) {
            router.get('applicationController').connectOutlet('topPanel', 'projectInfo');
            router.get('applicationController').connectOutlet('midPanel', 'projectSearchForm');
            router.get('applicationController').connectOutlet('bottomPanel', 'projectSearchResults');
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
        connectOutlets : function(router, event) {
            router.get('applicationController').connectOutlet('topPanel', 'home');
            router.get('applicationController').connectOutlet('midPanel', 'empty');
            router.get('applicationController').connectOutlet('bottomPanel', 'empty');
        }
    }),
    projects : App.ProjectRoute
});

App.Router = Em.Router.extend({
    root : App.RootRoute
});

$(function() {
    App.initialize();
});

