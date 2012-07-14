var AppRouter = Backbone.Router.extend({

    routes: {
        ""                  	: "list",
        "projects/page/:page"	: "list",
        "projects/add"         	: "addProject",
        "projects/:id"        	: "projectDetails",
        "about"             	: "about"
    },

    initialize: function () {
        //this.headerView = new HeaderView();
        //$('.header').html(this.headerView.el);
    },

	list: function(page) {
        var p = page ? parseInt(page, 5) : 1;
        var projectList = new ProjectCollection();
        projectList.fetch({success: function(){
            $("#list").html(new ProjectListView({model: projectList, page: p}).el);
        }});
        this.headerView.selectMenuItem('home-menu');
    },

    projectDetails: function (id) {
        var project = new Project({id: id});
        project.fetch({success: function(){
            $("#details").html(new ProjectView({model: project}).el);
        }});
        this.headerView.selectMenuItem();
    },

	addProject: function() {
        var project = new Project();
        $('#content').html(new ProjectView({model: project}).el);
        this.headerView.selectMenuItem('add-menu');
	},

    about: function () {
        if (!this.aboutView) {
            this.aboutView = new AboutView();
        }
        $('#content').html(this.aboutView.el);
        this.headerView.selectMenuItem('about-menu');
    }

});

utils.loadTemplate(['HeaderView', 'ProjectView', 'ProjectListItemView', 'AboutView'], function() {
    app = new AppRouter();
    Backbone.history.start();
});