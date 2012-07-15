// Have a NameSpaced App
var BlueApp = Bluebone;

BlueApp.views.add('TopMenu', {
    tpl: 'TopMenu',
    el: '#topmenu'
});

BlueApp.models.addApiResource('Project', {url: '/projects/api/project'});

BlueApp.widgets.add('RecentProjects');
BlueApp.widgets.add('About');
BlueApp.widgets.add('New', {tpl: 'About'});

BlueApp.views.add('Project', {model: 'Project'});

BlueApp.routers.Main = new (Bluebone.Router.extend({
    routes: {
		""			 		: "home",
        "projects/:id"  	: "project",
    },

    initialize: function () {
        BlueApp.views.TopMenu.renderTo('#topmenu');
    },
    
    project: function(id) {
    	var project = new BlueApp.models.Project({id: id});
	   	//BlueApp.views.Project.renderTo('#toppanel');
			   	
    }
		
}));

Backbone.history.start();
