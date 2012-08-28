/* Projects */
App.ProjectDetailController = Em.Controller.extend({
});

App.ProjectHomeView = Em.View.extend({
  templateName : 'project-home'
});

App.ProjectInfoView = Em.View.extend({
  templateName : 'project-info'
});


App.ProjectSearchFormView = Em.View.extend({
  templateName : 'project-search-form'
});

App.ProjectSearchResultsView = Em.View.extend({
  templateName : 'project-search-results'
});


// Adding transitions
App.RootRoute.reopen({
  gotoProjectInfo: function(router, event) {
      router.transitionTo('projects.info');
    }
});

// Adding routes to /projects
App.ProjectRoute.reopen({
  info : Em.Route.extend({
    route : '/info',
    connectOutlets : function(router, event) {
      router.get('applicationController').connectOutlet('topPanel', 'projectInfo');
      router.get('applicationController').connectOutlet('midPanel', 'projectSearchForm');
      router.get('applicationController').connectOutlet('bottomPanel', 'projectSearchResults');
    }
  })
});


//TODO: make sure that we update the router here
App.updateRouter();
