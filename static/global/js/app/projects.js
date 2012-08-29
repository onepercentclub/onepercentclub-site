/*
 * Project Search and List
 */
// FIXME: We're not using this Model right now.
App.ProjectPreviewModel = Em.Object.extend({
});


App.ProjectSearchController = Em.ArrayController.create({
    query: {
        order: 'alphabetically',
        limit: 4
    },

    content: [],

    init: function() {
        this._super();
        this.populate();
    },

    populate: function() {
        var controller = this;
        require(['app/data_source'], function(){
            //
            App.dataSource.get('project', controller.query, function(data) {
                controller.set('content', data['objects']);
            });
        });
    }
});


App.ProjectSearchFormView = Em.CollectionView.extend({
    templateName: 'project-search-form'
});

App.ProjectSearchResultsView = Em.CollectionView.extend({
    templateName: 'project-search-results',
    contentBinding: 'App.ProjectSearchController',
    itemViewClass: 'App.ProjectPreviewView',
    tagName: 'ul',
    classNames: 'list'
});

App.ProjectPreviewView  = Em.View.extend({
    tagName: 'li',
    templateName: 'project-preview',
    classNames: ['project-mid']
    // FIXME: We're going to handle clicks with Ember's target/action.
    // click: function(){
    //    ProjectApp.ApplicationController.projectId = this.content.id;
    // }
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
