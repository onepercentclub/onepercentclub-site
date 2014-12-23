/**
 *  Router Map
 */

App.Router.map(function(){
    this.resource('partner', {path: '/pp/:partner_id'}, function(){
        this.route('index', {path: '/'});
        this.route('projects', {path: '/projects'});
    });
	this.resource('business');
    this.resource('crowdfunding');
    this.resource('civic-crowdfunding');
});

App.PartnerRoute = Em.Route.extend(App.SubMenuMixin, {
    beforeModel: function (transition) {
        var partner_id = transition.params.partner_id;
        this.set('partner_id', partner_id);
        if (partner_id == 'cheetah'){
            this.set('subMenu', partner_id + '/menu');
        } else {
            this.set('subMenu', null);

        }
    },

    model: function (params, transition) {
        return App.Partner.find(params.partner_id);
    }
});


App.PartnerIndexRoute = Em.Route.extend({
    model: function (params, transition) {
        return this.modelFor('partner');
    },

    actions: {
        partnerProject: function () {
            this.transitionTo('myProject', 'pp:' + this.modelFor('partner').get('id'));
        }
    }
});


App.PartnerProjectsRoute = Em.Route.extend(App.ScrollToTop, {
    model: function (params, transition) {
        return this.modelFor('partner');
    }
});

App.BusinessRoute = Em.Route.extend(App.ScrollToTop);
App.CrowdfundingRoute = Em.Route.extend(App.ScrollToTop);
App.CivicCrowdfundingRoute = Em.Route.extend(App.ScrollToTop);