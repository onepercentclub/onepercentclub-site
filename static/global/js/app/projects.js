/*
 * Project Search and List
 */
// FIXME: We're not using this Model right now.
App.ProjectPreviewModel = Em.Object.extend({
});


App.projectSearchController = Em.ArrayController.create({
    query: {
        order: 'alphabetically',
        limit: 4
    },

    searchResults: null,

    filteredRegions: null,

    filteredCountries: null,

    init: function() {
        this._super();
        this.populate();
    },

    populate: function() {
        var controller = this;
        require(['app/data_source'], function(){

            App.dataSource.get('projectpreview', controller.query, function(data) {
                controller.set('searchResults', data['objects']);
            });

            App.dataSource.get('projectsearchform', controller.query, function(data) {
                var objects = data['objects'];
                for (var i = 0; i < objects.length; i++) {
                    switch (objects[i].name) {
                        case "countries":
                            controller.set('filteredCountries', objects[i].options);
                            break;
                        case "regions":
                            controller.set('filteredRegions', objects[i].options);
                            break;
                        case "text":
                            console.log("Text Search not implemented yet.");
                            break;
                        default:
                            console.log("Ignoring unknown project search element: " + objects[i].name);
                            break;
                    }
                }

            });

        });
    }
});

/* The search form. */
App.ProjectSearchFormView = Em.View.extend({
    tagName : 'form',
    templateName: 'project-search-form',
    classNames: ['search']
});

App.ProjectSearchTextField = Ember.TextField.extend({
    change: function (evt) {
        console.log("ProjectSearchTextField change event fired");
    }
});


/* The search results. */
App.ProjectSearchResultsView = Em.CollectionView.extend({
    tagName: 'ul',
    templateName: 'project-search-results',
    classNames: ['row'],

    contentBinding: 'App.projectSearchController.searchResults',
    itemViewClass: 'App.ProjectPreviewView'
});

App.ProjectPreviewView  = Em.View.extend({
    tagName: 'li',
    templateName: 'project-preview',
    classNames: ['project-mid', 'grid_1', 'column']

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
