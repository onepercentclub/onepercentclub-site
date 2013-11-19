/**
 *  Router Map
 */

App.Router.map(function(){
    this.resource('fundRaiser', {path: '/fundraisers/:fundraiser_id'});

    this.resource('myFundRaiserList', {path: '/my/fundraisers'});
    this.resource('myFundRaiserNew', {path: '/my/fundraisers/new/:project_id'});
    this.resource('myFundRaiser', {path: '/my/fundraisers/:my_fundraiser_id'});
});


/**
 * Fundraiser Routes
 */

App.FundRaiserRoute = Em.Route.extend(App.ScrollToTop, {
    model: function(params) {
        return App.FundRaiser.find(params.fundraiser_id);
    },

    setupController: function(controller, fundraiser) {
        this._super(controller, fundraiser);

        var project_id = fundraiser.get('project');
        controller.set('projectModel', App.ProjectPreview.find({project: project_id}));
// TODO: Add meta data when ready in sprint.
//
//        // Set the controller to show Project Supporters
//        var projectSupporterListController = this.controllerFor('projectSupporterList');
//        projectSupporterListController.set('supporters', App.DonationPreview.find({project: project.get('id')}));
//        projectSupporterListController.set('page', 1);
//        projectSupporterListController.set('canLoadMore', true);
    }
});


App.MyFundRaiserListRoute = Em.Route.extend(App.ScrollToTop, {
    model: function(params) {
        return App.FundRaiser.find();
    },
    setupController: function(controller, model) {
        this._super(controller, model);
    }
});


App.MyFundRaiserNewRoute = Em.Route.extend(App.ScrollToTop, {
    model: function(params) {
        // Using project preview to have less data attached (TODO: Verify!)
        var store = this.get('store');

        return store.createRecord(App.FundRaiser, {project: params.project_id});
    },
    setupController: function(controller, fundRaiser) {
        this._super(controller, fundRaiser);

        // Make project available in template.
        controller.set('fullProject', App.Project.find(fundRaiser.get('project')));
    }
});


App.MyFundRaiserRoute = Em.Route.extend({
    model: function(params) {
        return App.FundRaiser.find(params.my_fundraiser_id);
    }
});
