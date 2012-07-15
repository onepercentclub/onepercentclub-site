var BlueApp = {
	models: {},
	collections: {},
	views: {}
}


var AppRouter = Backbone.Router.extend({

    routes: {
        "projects/search/:params"	: "projectSearch",
        "projects/page/:page"	: "projectList",
        "projects/add"         	: "addProject",
        "projects/:id"        	: "projectDetails",
        "about"             	: "about"
    },

    initialize: function () {
        this.headerView = new HeaderView();
        $('.header').html(this.headerView.el);
    },

	projectList: function(page) {
        var p = page ? parseInt(page, 5) : 1;
        var projectList = new ProjectCollection();
        projectList.fetch({success: function(){
            $("#list").html(new ProjectListView({model: projectList, page: p}).el);
        }});main
        this.headerView.selectMenuItem('home-menu');
    },

	projectSearch: function(page, params) {
        var p = page ? parseInt(page, 5) : 1;
        var projectList = new ProjectCollection();
        projectList.fetch({success: function(){
            $("#list").html(new ProjectListView({model: projectList, params: paramas}).el);
        }});main
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
    BlueApp.Router = new AppRouter();
    Backbone.history.start();
});