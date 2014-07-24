/**
 *  Router Map
 */

App.Router.map(function(){
	this.resource('partner', {path: '/pp/:partner_id'});
});


App.PartnerRoute = Em.Route.extend(App.SubMenuMixin, {
    subMenu: 'cheetah/menu'
});