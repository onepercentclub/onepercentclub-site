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

BlueApp.views.add('Project');

BlueApp.routers.Main = new (Bluebone.Router.extend({
    routes: {
        ""                  : "home",
        "projects/:id"      : "project",
    },

    initialize: function () {
        console.log('Initializing BlueApp');
    },

    project: function(id) {
        var project = new BlueApp.models.Project({id: id});
        project.fetch({
            success: function(){
                BlueApp.views.Project.renderTo('#toppanel', project);
            }
        });

    }

}));

Backbone.history.start();
