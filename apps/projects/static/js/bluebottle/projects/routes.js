/**
 *  Router Map
 */

App.Router.map(function(){
    this.resource('projectList', {path: '/projects'}, function() {
        this.route('new');
        this.route('search');
    });

   this.resource('project', {path: '/projects/:project_id'}, function() {
        this.resource('projectPlan', {path: '/plan'});
        this.resource('projectTasks', {path: '/tasks'}, function(){
            this.resource('projectTask', {path: '/:task_id'});
            this.resource('projectTaskNew', {path: '/new'});
            this.resource('projectTaskEdit', {path: '/:task_id/edit'});
        });
    });

    this.resource('myProject', {path: '/my/projects/:my_project_id'}, function() {
        this.resource('myProjectPlan', {path: 'plan'}, function() {
            this.route('index');
            this.route('basics');
            this.route('location');
            this.route('description');
            this.route('media');

            this.route('organisation');
            this.route('legal');
            this.route('ambassadors');

            this.route('bank');
            this.route('campaign');
            this.route('budget');

            this.route('submit');

        });

        this.resource('myProjectPlanReview', {path: 'plan/review'});
        this.resource('myProjectPlanApproved', {path: 'plan/approved'});
        this.resource('myProjectPlanRejected', {path: 'plan/rejected'});

        this.resource('myProjectPitch', {path: 'pitch'}, function() {
            this.route('index');
            this.route('basics');
            this.route('location');
            this.route('media');

            this.route('submit');
        });
        this.resource('myProjectPitchReview', {path: 'pitch/review'});
        this.resource('myProjectPitchApproved', {path: 'pitch/approved'});
        this.resource('myProjectPitchRejected', {path: 'pitch/rejected'});

        this.resource('myProjectCampaign', {path: 'campaign'});

    });

    this.resource('myPitchNew', {path: '/my/pitch/new'});
    this.resource('myProjectList', {path: '/my/projects'});
    this.resource('partner', {path: '/pp/:partner_organization_id'});

});


/**
 * Project Routes
 */

App.ProjectRoute = Em.Route.extend(App.ScrollToTop, {
    model: function(params) {
        var page =  App.Project.find(params.project_id);
        var route = this;
        page.on('becameError', function() {
            //route.transitionTo('error.notFound');
            route.transitionTo('projectList');
        });
        return page;
    },

    setupController: function(controller, project) {
        this._super(controller, project);

        // Set the controller to show Project Supporters
        var projectSupporterListController = this.controllerFor('projectSupporterList');
        projectSupporterListController.set('supporters', App.DonationPreview.find({project: project.get('id')}));
        projectSupporterListController.set('page', 1);
        projectSupporterListController.set('canLoadMore', true);
    }
});


// This is the 'ProjectWallPostListRoute'
App.ProjectIndexRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('project');
    },

    setupController: function(controller, model) {
        // Empty the items and set page to 0 if project changes so we don't show wall posts from previous project
        if (this.get('model_id') != model.get('id')) {
            controller.set('items', Em.A());
            controller.set('page', 0);
        }
        this.set('model_id', model.get('id'));
        this._super(controller, model.get('wallposts'));
    }
});


App.ProjectPlanRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('project').get('plan');
    }
});



/**
 * My Projects
 * - Manage your project(s)
 */

App.MyProjectListRoute = Em.Route.extend({
    model: function(params) {
        return App.MyProject.find();
    },
    setupController: function(controller, model) {
        this._super(controller, model);
    }

});


App.MyPitchNewRoute = Em.Route.extend({
    model: function() {
        var store = this.get('store');
        return store.createRecord(App.MyProject);
    }
});


App.MyProjectRoute = Em.Route.extend({
    // Load the Project
    model: function(params) {
        return App.MyProject.find(params.my_project_id);
    }
});


App.MyProjectPitchRoute =  Em.Route.extend({
    model: function(params) {
        return this.modelFor('myProject').get('pitch');
    }
});


App.MyProjectPitchSubRoute = Ember.Route.extend({
    redirect: function() {
        var status = this.modelFor('myProject').get('pitch.status');
        switch(status) {
            case 'submitted':
                this.transitionTo('myProjectPitchReview');
                break;
            case 'rejected':
                this.transitionTo('myProjectPitchRejected');
                break;
            case 'approved':
                this.transitionTo('myProjectPitchApproved');
                break;
        }
    },
    model: function(params) {
        return this.modelFor('myProject').get('pitch');
    },
    exit: function() {
        if (this.get('controller')) {
            this.get('controller').stopEditing();
        }
    }

});


App.MyProjectPitchBasicsRoute = App.MyProjectPitchSubRoute.extend({});
App.MyProjectPitchLocationRoute = App.MyProjectPitchSubRoute.extend({});
App.MyProjectPitchMediaRoute = App.MyProjectPitchSubRoute.extend({});
App.MyProjectPitchSubmitRoute = App.MyProjectPitchSubRoute.extend({});

App.MyProjectPitchIndexRoute =  Em.Route.extend({
    redirect: function() {
        var status = this.modelFor('myProject').get('pitch.status');
        switch(status) {
            case 'submitted':
                this.transitionTo('myProjectPitchReview');
                break;
            case 'rejected':
                this.transitionTo('myProjectPitchRejected');
                break;
            case 'approved':
                this.transitionTo('myProjectPitchApproved');
                break;
        }
    },
    model: function(params) {
        return this.modelFor('myProject').get('pitch');
    }
});


App.MyProjectPitchReviewRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('myProject').get('pitch');
    }
});


// My ProjectPlan routes

App.MyProjectPlanRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('myProject').get('plan');
    }
});

App.MyProjectPlanSubRoute = Em.Route.extend({
    redirect: function() {
        var status = this.modelFor('myProject').get('plan.status');
        switch(status) {
            case 'submitted':
                this.transitionTo('myProjectPlanReview');
                break;
            case 'rejected':
                this.transitionTo('myProjectPlanRejected');
                break;
            case 'approved':
                this.transitionTo('myProjectPlanApproved');
                break;
        }
    },

    model: function(params) {
        return this.modelFor('myProject').get('plan');
    },

    exit: function() {
        if (this.get('controller')) {
            this.get('controller').stopEditing();
        }
    }
});

App.MyProjectPlanBasicsRoute = App.MyProjectPlanSubRoute.extend({});
App.MyProjectPlanDescriptionRoute = App.MyProjectPlanSubRoute.extend({});
App.MyProjectPlanLocationRoute = App.MyProjectPlanSubRoute.extend({});
App.MyProjectPlanMediaRoute = App.MyProjectPlanSubRoute.extend({});
//App.MyProjectPlanAmbassadorsRoute = App.MyProjectPlanSubRoute.extend({});
App.MyProjectPlanSubmitRoute = App.MyProjectPlanSubRoute.extend({});

App.MyProjectPlanCampaignRoute = App.MyProjectPlanSubRoute.extend({});
App.MyProjectPlanBudgetRoute = App.MyProjectPlanSubRoute.extend({});

App.MyProjectPlanOrganisationRoute = App.MyProjectPlanSubRoute.extend({

    setupController: function(controller, model) {
        this._super(controller, model);
        var organization = model.get('organization');

        organization.one('didLoad', function(){
            if (organization.get('addresses.length') == 0) {
                controller.send('addAddress');
            }
            controller.set('address', model.get('organization.addresses.firstObject'));
        });

        if (!organization){
            controller.set('organizations', App.MyOrganization.find());
        }
    }
});

App.MyProjectPlanBankRoute = App.MyProjectPlanSubRoute.extend({});


App.MyProjectPlanLegalRoute = App.MyProjectPlanSubRoute.extend({});


App.MyProjectPlanIndexRoute = Ember.Route.extend({
    redirect: function() {
        var status = this.modelFor('myProject').get('plan.status');
        switch(status) {
            case 'submitted':
                this.transitionTo('myProjectPlanReview');
                break;
            case 'rejected':
                this.transitionTo('myProjectPlanRejected');
                break;
            case 'approved':
                this.transitionTo('myProjectPlanApproved');
                break;
        }
    },

    model: function(params) {
        return this.modelFor('myProject').get('plan');
    }
});


App.MyProjectPlanReviewRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('myProject').get('plan');
    }
});

App.MyProjectCampaignRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('myProject');
    }
});

