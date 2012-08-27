(function() {

  // Create the application
  window.App = Em.Application.create({
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
    }),

    /* Projects */
    ProjectDetailController : Em.Controller.extend({
    }),

    ProjectHomeView : Em.View.extend({
      templateName : 'project-home'
    }),

    ProjectSearchFormView : Em.View.extend({
      templateName : 'project-search-form'
    }),

    ProjectSearchResultsView : Em.View.extend({
      templateName : 'project-search-results'
    }),


    /* Routing */
    Router : Em.Router.extend({
      root : Em.Route.extend({
        // Used for navigation
        gotoHome : function(router, event) {
          router.transitionTo('home');
        },
        gotoProjects : function(router, event) {
          router.transitionTo('projects');
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
        projects : Em.Route.extend({
          route : '/projects',
          connectOutlets : function(router, event) {
            router.get('applicationController').connectOutlet('topPanel', 'projectHome');
            router.get('applicationController').connectOutlet('midPanel', 'projectSearchForm');
            router.get('applicationController').connectOutlet('bottomPanel', 'projectSearchResults');
          }
        }),
      })
    })

  });

  $(function() {
    App.initialize();
  });


})();
