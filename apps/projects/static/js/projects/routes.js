App.Router.map(function(){
    this.resource('myProject', {path: '/my/projects/:id'}, function() {
        this.route('goal');
    });
    this.resource('projectMpesaList', {path: '/project/:project_id/mpesa'});
});

App.MyProjectRoute.reopen(App.AuthenticatedRouteMixin, {
    // Load the Project
    model: function(params) {
        var match = params.id.match(/pp:(.*)/);

        if (match && match.length === 2) {
          var partner = App.Partner.find(match[1]),
              project = App.MyProject.createRecord({partner: partner});

          return project;
        } else {
          return this._super(params);
        }
    },

    afterModel: function (model, transition) {
        this._super();


        // Track project create via partner organization
        var tracker = this.get('tracker'),
            partner = model.get('partner');

        if (tracker && partner) {
            tracker.trackEvent("Create Partner Campaign", {partner: partner.get('name')});
        }
    }
});

App.MyProjectStartRoute.reopen({
    googleConversion:{
        label: 'HQPlCJL-6wsQ7o7O1gM'
    }

});

App.MyProjectListRoute.reopen(App.AuthenticatedRouteMixin, {});
App.MyProjectSubRoute.reopen(App.AuthenticatedRouteMixin, {});
App.MyProjectGoalRoute = App.MyProjectSubRoute.extend(App.TrackRouteActivateMixin, {
    trackEventName: 'Create Campaign - Goal'
});
