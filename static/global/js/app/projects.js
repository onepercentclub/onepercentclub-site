/*
 * Project Search and List
 */
App.projectPreviewModel = Em.Object.create({
    url: 'project'
});


App.ProjectSearchController = Em.Object.create({
    query: {
        order: 'alphabetically',
        limit: 4
    },

    content: null,

    init: function() {
        this.populate();
    },

    populate: function() {
        var controller = this;
        require(['app/data_source'], function(){
            App.dataSource.get(App.projectPreviewModel.url, controller.query, function(data) {
                controller.set('content', data['objects']);
            });
        });
    }
});


App.ProjectPreviewView = Em.View.extend({
    templateName: 'project-preview'
});

App.ProjectSearchFormView = Em.View.extend({
    templateName: 'project-search-form'
});

App.ProjectSearchResultsView = Em.View.extend({
    templateName: 'project-search-results'
});


/*
 * Project Detail
 */
App.projectModel = Em.Object.create({
    url:'projectdetail'
});


App.projectController = Em.Controller.create({
});


App.ProjectDetailView = Em.View.extend({
    templateName:'project-detail'
});
