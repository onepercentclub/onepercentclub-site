/**
 *  Router Map
 */

App.Router.map(function(){
	this.resource('partner', {path: '/pp/:partner_id'});
});


App.PartnerRoute = Em.Route.extend(App.SubMenuMixin, {
    subMenu: 'cheetah/menu',

    beforeModel: function (transition) {
        this.set('partner_id', transition.params.partner_id);
    },

    actions: {
        partnerProject: function () {
            this.transitionTo('myProject', 'pp:' + this.get('partner_id'));
        }
    }
});