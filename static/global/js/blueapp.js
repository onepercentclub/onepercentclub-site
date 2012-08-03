var BlueApp = Bluebone;

// we want the side-effect of creating the object
BlueApp.getListView('ProjectsSearchResults', {
    resource: 'Project',
    itemView: 'ProjectSearchItem',
    url: '/projects/api/project/',
    order: 'title',
    tpl: 'ProjectSearch'
});

// we want the side-effect of creating the object
BlueApp.getView('ProjectSearchForm');

BlueApp.setAfterRender(function(el){
	init(el);
});


BlueApp.routers.Main = new (Bluebone.Router.extend({
    routes: {
        ""                            : "home",
        "projects/:slug/"             : "project",
        "projects/:slug/map/"         : "projectMap",
        "projects/search/?:params"    : "projectSearch"
    },

    initialize: function () {
        console.log('Initializing BlueApp');
    },


    project: function(slug) {
        var url = '/projects/' + slug;
        BlueApp.renderSnippetTo('#toppanel', url);
    },


    projectMap: function(slug) {
        var url = '/projects/' + slug + '/map';
        BlueApp.renderSnippetTo('#toppanel', url);
    },

	projectSearch: function(params) {
		var components = params.split("&");
		var params = {};
		for (c in components) {
			var d = components[c].split("=");
			params[d[0]] = d[1];
		}
		BlueApp.views.ProjectsSearchResults.renderTo('#ProjectsSearchResults', params);
	}
}));

Backbone.history.start();
