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

    searchResults: null,

    searchFormElements: null,

    init: function() {
        this._super();
        this.populate();
    },

    populate: function() {
        var controller = this;
        require(['app/data_source'], function(){
            //
            App.dataSource.get('project', controller.query, function(data) {
                controller.set('searchResults', data['objects']);
            });
            App.dataSource.get('projectsearchform', controller.query, function(data) {
                controller.set('searchFormElements', data['objects']);
            });

        });
    }
});

/* The search form. */
App.ProjectSearchFormView = Em.CollectionView.extend({
    tagName : 'form',
    templateName: 'project-search-form',
    classNames: ['search', 'row'],

    contentBinding: 'App.ProjectSearchController.searchFormElements',
    itemViewClass: 'App.ProjectSearchFilterElementView'
});

App.ProjectSearchFilterElementView = Em.View.extend({
    tagName: 'div',
    templateName: 'project-search-form-element',
    classNames: ['form-element', 'column', 'grid_1']
});

/* The search results. */
App.ProjectSearchResultsView = Em.CollectionView.extend({
    tagName: 'ul',
    templateName: 'project-search-results',
    classNames: ['list'],

    contentBinding: 'App.ProjectSearchController.searchResults',
    itemViewClass: 'App.ProjectPreviewView'
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
