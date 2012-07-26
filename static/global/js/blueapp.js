// Have a NameSpaced App
var BlueApp = Bluebone;

BlueApp.views.add('TopMenu');

BlueApp.views.addList('RecentProjects', {
    resource: 'Project',
    itemView: 'ProjectListItem',
    url: '/projects/api/project/'
});

BlueApp.views.add('About');

BlueApp.views.add('New', {tpl: 'About'});

BlueApp.views.addList('ProjectMembers', {
	resource: 'ProjectMembers',
	itemView: 'MemberListItem',	
    url: '/projects/api/projectmembers/',
});


BlueApp.views.add('Project');


BlueApp.views.addList('LatestProjects', {
    resource: 'Project',
    itemView: 'ProjectSearchItem',
    url: '/projects/api/project/',
    order: '-created',
    tpl: 'ProjectSearch',
});

BlueApp.views.addList('ProjectsSearchResults', {
    resource: 'Project',
    itemView: 'ProjectSearchItem',
    url: '/projects/api/project/',
    order: 'title',
    tpl: 'ProjectSearch',
});

BlueApp.views.add('ProjectSearchForm');


BlueApp.snippets.setCallback(function(el){
	init(el);
});

BlueApp.views.setCallback(function(el){
	init(el);
});


BlueApp.routers.Main = new (Bluebone.Router.extend({
    routes: {
        ""                    : "home",
        "projects/:slug/"     : "project",
        "projects/:slug/map/" : "projectMap",
        "project/search/?:params"	  : "projectSearch",
    },

    initialize: function () {
        console.log('Initializing BlueApp');
    },
	

    project: function(slug) {
	    BlueApp.snippets.renderTo('#toppanel', '/projects/' +  slug );
    },


    projectMap: function(slug) {
    	var url = '/projects/' + slug + '/map';
    	BlueApp.snippets.renderTo('#toppanel', url);
    },

	projectSearch: function(params) {
		var components = params.split("&");
		var params = {};
		for (c in components) {
			var d = components[c].split("=");
			params[d[0]] = d[1];
		}
		BlueApp.views.ProjectsSearchResults.renderTo('.searchResults', params)
	}
	

}));

Backbone.history.start();
