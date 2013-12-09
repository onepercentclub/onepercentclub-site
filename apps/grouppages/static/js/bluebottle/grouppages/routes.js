App.Router.map(function(){
    this.resource('groupPages', {path: '/groups'}, function() {
        this.resource('group', {path: '/:group_id'});
    });
});


App.GroupListRoute = Em.Route.extend(App.ScrollToTop, {
    model: function(params) {
        return  App.GroupPage.find();
    }
});


App.GroupRoute = Em.Route.extend(App.ScrollToTop, {
    model: function(params) {
        return  App.GroupPage.find(params.group_id);
    }
});
