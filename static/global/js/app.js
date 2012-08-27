(function() {

  // Create the application
  window.App = Ember.Application.create({
    rootElement : '#content',

    // Define the main application controller. This is automatically picked up by
    // the application and initialized.
    ApplicationController : Ember.Controller.extend({
    }),

    ApplicationView : Ember.View.extend({
      templateName : 'application'
    }),

    // Use this to clear an outlet
    EmptyView : Ember.View.extend({
      template : ''
    }),

    /* Home */
    HomeView : Ember.View.extend({
      templateName : 'home'
    }),

    /* Projects */
    ProjectsController : Ember.Controller.extend({
    }),

    ProjectsHomeView : Ember.View.extend({
      templateName : 'projects-home'
    }),

    ProjectsSearchFormView : Ember.View.extend({
      templateName : 'projects-search-form'
    }),

    ProjectsSearchResultsView : Ember.View.extend({
      templateName : 'projects-search-results'
    }),

    /* Routing */
    Router : Ember.Router.extend({
      root : Ember.Route.extend({
        // Used for navigation
        gotoHome : function(router, event) {
          router.transitionTo('home');
        },
        gotoProjects : function(router, event) {
          router.transitionTo('projects');
        },
        // The actual routing
        home : Ember.Route.extend({
          route : '/',
          connectOutlets : function(router, event) {
            router.get('applicationController').connectOutlet('topPanel', 'home');
            router.get('applicationController').connectOutlet('midPanel', 'empty');
            router.get('applicationController').connectOutlet('bottomPanel', 'empty');
          }
        }),
        projects : Ember.Route.extend({
          route : '/projects',
          connectOutlets : function(router, event) {
            router.get('applicationController').connectOutlet('topPanel', 'projectsHome');
            router.get('applicationController').connectOutlet('midPanel', 'projectsSearchForm');
            router.get('applicationController').connectOutlet('bottomPanel', 'projectsSearchResults');
          }
        }),
      })
    })

  });

  $(function() {
    App.initialize();
  });

})(); 