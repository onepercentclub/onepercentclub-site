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

    setupController: function(controller, project) {
        this._super(controller, project);
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
        var project = App.Project.find(params.project_id);

        var store = this.get('store');
        return store.createRecord(App.FundRaiser, {project: project});
    }
});


App.MyFundRaiserRoute = Em.Route.extend({
    model: function(params) {
        return App.FundRaiser.find(params.my_fundraiser_id);
    }
});
