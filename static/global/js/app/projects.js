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
    searchResultsMeta: [],

    filteredRegions: null,

    filteredCountries: null,

    init: function() {
        this._super();
        this.populate();
    },

    nextSearchResult: function() {
        var meta  = this.get('searchResultsMeta');
        next = (RegExp('offset=' + '(.+?)(&|$)').exec(meta.next)||[,null])[1]
        return next;
    }.property('searchResultsMeta'),
    
    previousSearchResult: function() {
        var meta  = this.get('searchResultsMeta');
        previous = (RegExp('offset=' + '(.+?)(&|$)').exec(meta.previous)||[,null])[1]
        return previous;
    }.property('searchResultsMeta'),
    
    populate: function() {
        var controller = this;
        require(['app/data_source'], function(){

            App.dataSource.get('projectpreview', controller.query, function(data) {
                controller.set('searchResults', data['objects']);
                controller.set('searchResultsMeta', data['meta']);
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
    classNames: ['search', 'row']
});

App.ProjectSearchTextField = Em.TextField.extend({
    change: function (evt) {
        console.log("ProjectSearchTextField change event fired");
    }
});


/* The search results. */
App.ProjectSearchResultsSectionView  = Em.View.extend({
    tagName: 'div',
    classNames: 'lightgray section results',
    templateName: 'project-search-results-section',
});


App.ProjectSearchResultsNextView = Em.View.extend({
  nextBinding : 'App.projectSearchController.nextSearchResult',
  template: '',
  tagName : 'div',
  classNames: 'paginator next',
  classNameBindings: ['disabled'],
  disabled: function(){
    if (this.next == null) return true;
    return false;
  }.property('next'),
  click: function(){
    if (this.next) {
      App.projectSearchController.changeFilterElement({
        searchFilter : 'offset',
        value : this.next
      })
    }
  }
});


App.ProjectSearchResultsPreviousView = Em.View.extend({
  previousBinding : 'App.projectSearchController.previousSearchResult',
  template: '',
  tagName : 'div',
  classNames: 'paginator previous',
  //TODO: Do hidden smarter (template?)
  classNameBindings: ['disabled'],
  disabled: function(){
    if (this.previous == null) return true;
    return false;
  }.property('previous'),
  //TODO: Use Ember solution
  click: function(){
    if (this.next) {
      App.projectSearchController.changeFilterElement({
        searchFilter : 'offset',
        value : this.next
      })
    }
  }
});


App.ProjectSearchResultsView = Em.CollectionView.extend({
    tagName: 'ul',
    templateName: 'project-search-results',
    classNames: ['list', 'row'],

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
