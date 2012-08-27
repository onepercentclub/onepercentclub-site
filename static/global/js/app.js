(function() {

// Create the application
window.App = Ember.Application.create({
  rootElement: '#content',

  // Define the main application controller. This is automatically picked up by
  // the application and initialized.
  ApplicationController: Ember.Controller.extend({
  }),
  
  ApplicationView: Ember.View.extend({
    templateName: 'application'
  }),


  HomeView: Ember.View.extend({
    templateName: 'home'
  }),


  Router: Ember.Router.extend({
    root: Ember.Route.extend({
      home: Ember.Route.extend({
        route: '/',
        connectOutlets: function(router, event) {
          router.get('applicationController').connectOutlet('topPanel', 'home');
        }
      }),
    })
  })

});

$(function() {
  App.initialize();
});

})();