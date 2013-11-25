/**
 *  Router Map
 */

App.Router.map(function() {
    this.resource('fundRaiser', {path: '/fundraisers/:fundraiser_id'}, function(){
    });
    this.resource('fundRaiserNew', {path: '/projects/:project_id/new-fundraiser'});

// TODO: Future resources.
//    this.resource('myFundRaiserList', {path: '/my/fundraisers'});
//    this.resource('myFundRaiser', {path: '/my/fundraisers/:my_fundraiser_id'});
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

        var project_id = fundraiser.get('project.id');
        controller.set('fundRaiseSupporters', App.DonationPreview.find({project: project_id, fundraiser: fundraiser.id}));
    }
});


App.FundRaiserIndexRoute = Em.Route.extend(App.ScrollToTop, {
    // This way the ArrayController won't hold an immutable array.
    setupController: function(controller, model) {
        var fundraiser_id = this.modelFor('fundRaiser').get('id');
        controller.set('page', 1);
        App.WallPost.find({'parent_type': 'fund raiser', 'parent_id': fundraiser_id}).then(function(items){
            controller.set('meta', items.get('meta'));
            controller.set('model', items.toArray());
        });
    }
});



App.FundRaiserNewRoute = Em.Route.extend(App.ScrollToTop, {
    model: function(params) {
        // Using project preview to have less data attached (TODO: Verify!)
        var store = this.get('store');

        var projectPreview = App.ProjectPreview.find(params.project_id);

        return store.createRecord(App.FundRaiser, {project: projectPreview});
    },
    setupController: function(controller, fundRaiser) {
        this._super(controller, fundRaiser);
    }
});

// TOOD: Unused at this time.
//App.MyFundRaiserListRoute = Em.Route.extend(App.ScrollToTop, {
//    model: function(params) {
//        return App.FundRaiser.find();
//    },
//    setupController: function(controller, model) {
//        this._super(controller, model);
//    }
//});
//
//
//App.MyFundRaiserRoute = Em.Route.extend({
//    model: function(params) {
//        return App.FundRaiser.find(params.my_fundraiser_id);
//    }
//});
