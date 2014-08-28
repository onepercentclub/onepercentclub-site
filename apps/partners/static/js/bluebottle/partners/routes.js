/**
 *  Router Map
 */

App.Router.map(function(){
	this.resource('partner', {path: '/pp/:partner_id'});
});


App.PartnerRoute = Em.Route.extend(App.SubMenuMixin, {
    beforeModel: function (transition) {
        var partner_id = transition.params.partner_id;

        this.set('partner_id', partner_id);
        this.set('subMenu', partner_id + '/menu');
    },

    actions: {
        partnerProject: function () {
            this.transitionTo('myProject', 'pp:' + this.get('partner_id'));
        }
    }
});
