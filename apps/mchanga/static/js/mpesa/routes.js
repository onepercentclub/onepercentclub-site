/**
 *  Router Map
 */

App.Router.map(function(){
    this.resource('projectDonationList', {path: '/projects/:project_id/donations'});

});

App.ProjectMpesaListRoute = Em.Route.extend({
    model: function(params) {
        var project_id = params.project_id.split('?')[0];
        return App.Project.find(project_id);
    },

    setupController: function(controller, project) {
        this._super(controller, project);
        controller.set('projectMpesaPayments', App.MpesaPayment.find({project: project.id}));

    }
});
