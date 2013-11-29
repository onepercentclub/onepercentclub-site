/**
 *  Router Map
 */

App.Router.map(function() {
    // The empty function is there for the fundRaiserIndex route to be called.
    this.resource('fundRaiser', {path: '/fundraisers/:fundraiser_id'}, function(){});

    this.resource('fundRaiserEdit', {path: '/fundraisers/:fundraiser_id/edit'});

    this.resource('fundRaiserNew', {path: '/projects/:project_id/new-fundraiser'});

    this.resource('myFundRaiserList', {path: '/my/fundraisers'});

// TODO: Future resources.
//    this.resource('myFundRaiser', {path: '/my/fundraisers/:my_fundraiser_id'});

    this.resource('fundRaiserDonationList', {path: '/fundraisers/:fundraiser_id/donations'});
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


App.FundRaiserIndexRoute = Em.Route.extend({
    // This way the ArrayController won't hold an immutable array thus it can be extended with more wall-posts.
    setupController: function(controller, model) {
        var parent_id = this.modelFor('fundRaiser').get('id');
        // Only reload this if switched to another fundraiser.
        if (controller.get('parent_id') != parent_id){
            controller.set('page', 1);
            controller.set('parent_id', parent_id);
            App.WallPost.find({'parent_type': 'fund raiser', 'parent_id': parent_id}).then(function(items){
                controller.set('meta', items.get('meta'));
                controller.set('model', items.toArray());
            });
        }
    }
});


App.FundRaiserNewRoute = Em.Route.extend(App.ScrollToTop, {
    model: function(params) {
        // Using project preview to have less data attached (TODO: Verify!)
        var store = this.get('store');

        var projectPreview = App.ProjectPreview.find(params.project_id);

        return store.createRecord(App.FundRaiser, {project: projectPreview});
    }
});

App.FundRaiserEditRoute = Em.Route.extend(App.ScrollToTop, {
    model: function(params) {
        return App.FundRaiser.find(params.fundraiser_id);
    }
});


App.FundRaiserDonationListRoute = Em.Route.extend({
    model: function(params) {
        return App.FundRaiser.find(params.fundraiser_id);
    },

    setupController: function(controller, fundraiser) {
        this._super(controller, fundraiser);

        var project_id = fundraiser.get('project.id');
        controller.set('fundRaiseDonations', App.ProjectDonation.find({project: project_id, fundraiser: fundraiser.id}));
    }
});


App.MyFundRaiserListRoute = Em.Route.extend(App.ScrollToTop, {
    model: function(params) {
        return App.CurrentUser.find('current').then(function(user) {
            var user_id = user.get('id_for_ember');
            return App.FundRaiser.find({owner: user_id});
        });
    },
    setupController: function(controller, model) {
        this._super(controller, model);
    }
});
//
// TOOD: Unused at this time.
//App.MyFundRaiserRoute = Em.Route.extend({
//    model: function(params) {
//        return App.FundRaiser.find(params.my_fundraiser_id);
//    }
//});
