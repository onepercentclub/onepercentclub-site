App.HomeRoute = Em.Route.extend(App.TrackRouteActivateMixin, {
    trackEventName: 'Homepage visit',

    model: function(params) {
        return App.HomePage.find(App.get('language'));
    }
});
