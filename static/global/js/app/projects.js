/*
 * Project Search and List
 */
// FIXME: We're not using this Model right now.
App.ProjectPreviewModel = Em.Object.extend({
});

App.ProjectModel = Em.Object.extend({
});


App.projectSearchController = Em.ArrayController.create({
    // The saved query state.
    query: {},

    // Project preview search results.
    searchResults: null,
    searchResultsMeta: [],

    // List of regions and countries returned from the search form filter.
    filteredRegions: [],
    filteredCountries: [],

    // The text, selected region and country to use when building the query.
    searchText: "",
    selectedRegion: null,
    selectedCountry: null,

    init: function() {
        this._super();
        this.populate();
    },


    // Computed properties used for pagination.
    nextSearchResult: function() {
        var meta  = this.get('searchResultsMeta');
        var next = (RegExp('offset=' + '(.+?)(&|$)').exec(meta.next)||[,null])[1]
        return next;
    }.property('searchResultsMeta'),
    
    previousSearchResult: function() {
        var meta  = this.get('searchResultsMeta');
        var previous = (RegExp('offset=' + '(.+?)(&|$)').exec(meta.previous)||[,null])[1]
        return previous;
    }.property('searchResultsMeta'),


    // Functions for loading the data.
    populate: function() {
        var controller = this;
        require(['app/data_source'], function(){
            var query = controller.get('query');

            // Get the project preview data using the current query.
            // We're limiting the number of returned items to 4.
            var projectPreviewQuery = $.extend({limit: 4}, query);
            App.dataSource.get('projectpreview', projectPreviewQuery, function(data) {
                controller.set('searchResults', data['objects']);
                controller.set('searchResultsMeta', data['meta']);
            });

            // Get the project search data using the same query.
            // Note that we're *not* limiting the number of returned items as above.
            App.dataSource.get('projectsearchform', query, function(data) {
                var objects = data['objects'];
                for (var i = 0; i < objects.length; i++) {
                    switch (objects[i].name) {
                        case "countries":
                            controller.set('filteredCountries', objects[i].options);
                            break;
                        case "regions":
                            controller.set('filteredRegions', objects[i].options);
                            break;
                        default:
                            break;
                    }
                }

            });

        });
    },

    // Updates the query and populates the data.
    update: function() {
        var query = this.get('query');

        // Add or remove the text query parameter.
        var searchText = this.get('searchText');
        if (searchText.length > 0) {
            query.text = searchText;
        } else {
            delete query.text;
        }

        // Add or remove the region query parameter.
        var selectedRegion = this.get('selectedRegion');
        if (selectedRegion != null && selectedRegion['id'].length > 0) {
            query.regions = selectedRegion['id'];
        } else {
            delete query.regions;
        }

        // Add or remove the country query parameter.
        var selectedCountry = this.get('selectedCountry');
        if (selectedCountry != null && selectedCountry['id'].length > 0) {
            query.countries = selectedCountry['id'];
        } else {
            delete query.countries;
        }

        // Set the query and re-populate the data.
        this.set('query', query);
    },

    // Updates the query based on the queryParam and populates the data.
    updateParam: function(queryParam, remove) {
        var query = this.get('query');
        var tempQuery = $.extend({}, query);

        // Delete the param if it's already in the query. This lets us update
        // the param or leave it deleted depending on what's requested.
        var i = 0;
        for (var property in queryParam) {
            if (i > 0) {
                break;  // Only use the first property in queryParam.
            }
            if (undefined != tempQuery[property]) {
                delete tempQuery[property];
            }
            i++;
        }

        // Create an updated query.
        if (remove) {
            var updatedQuery = tempQuery;
        } else {
            var updatedQuery = $.extend(queryParam, tempQuery);
        }

        // Set the updated query.
        this.set('query', updatedQuery);
    },

    /* Methods to handle specific interactions from the UI */
    submitSearchForm: function(event) {
        this.updateParam({'offset': null}, true); // delete offset param
        this.update();
        this.populate();
    },

    clickPrevNext: function(event, offset) {
        var param = {};
        param['offset'] = offset;
        this.updateParam(param);
        this.populate();
    }

});

/* The search form. */
App.ProjectSearchFormView = Em.View.extend({
    tagName : 'form',
    templateName: 'project-search-form',
    classNames: ['search'],

    submit: function(event) {
        // inspired by http://jsfiddle.net/dgeb/RBbpS/
        event.preventDefault();
        App.projectSearchController.submitSearchForm(event);
//        We want to do something generic like this:
//
//        this.get('controller').update();
//        this.get('controller').addPerson(this.getPath('textField.value'));
//        this.setPath('textField.value', null);
//
//        This can't be done right now because the tplhandlebars doesn't support
//        anonymous handlebar scripts which means we can't define a controllerBinding
//        in the template:
//
//          {{#view App.ProjectSearchFormView controllerBinding="App.projectSearchController"}}
//
//        We can either (1) add anonymous handlebar scripts into the tplhandlebars django
//        template tag or (2) create the anonymous handlebar scripts in HTML and load
//        them manually. The best option is probably (2) because we want that functionality
//        for other reasons.

    }
});


/* The search results. */
App.ProjectSearchResultsSectionView  = Em.View.extend({
    tagName: 'div',
    classNames: ['lightgray', 'section', 'results'],
    templateName: 'project-search-results-section'
});


App.ProjectSearchResultsNextView = Em.View.extend({
    tagName: 'div',
    classNames: ['paginator', 'next'],

    nextBinding: 'App.projectSearchController.nextSearchResult',
    //TODO: Do hidden smarter (template?)
    classNameBindings:['disabled'],

    disabled: function () {
        if (this.next == null) return true;
        return false;
    }.property('next'),

    click: function(event) {
        if (this.next) {
            // TODO: Can we make this independent of the controller?
            App.projectSearchController.clickPrevNext(event, this.next);
        }
    }
});


App.ProjectSearchResultsPreviousView = Em.View.extend({
    tagName: 'div',
    classNames: ['paginator', 'previous'],

    previousBinding: 'App.projectSearchController.previousSearchResult',
    // TODO: Do hidden smarter (template?)
    classNameBindings: ['disabled'],

    disabled: function() {
        if (this.previous == null) return true;
        return false;
    }.property('previous'),

    click: function(event) {
        if (this.previous) {
            // TODO: Can we make this independent of the controller?
            App.projectSearchController.clickPrevNext(event, this.previous);
        }
    }
});


App.ProjectSearchResultsView = Em.CollectionView.extend({
    tagName: 'ul',
    templateName: 'project-search-results',
    classNames: ['row'],

    contentBinding: 'App.projectSearchController.searchResults',
    itemViewClass: 'App.ProjectPreviewView'
});

App.ProjectPreviewView = Em.View.extend({
    tagName: 'li',
    templateName: 'project-preview',
    classNames: ['project-mid', 'grid_1', 'column']
});

App.ProjectSearchSelect = Em.Select.extend({
    change: function(event){
        App.projectSearchController.submitSearchForm(event);
    }
});


App.ProjectStartView = Em.View.extend({
    templateName:'project-start'
});



/*
 * Project Detail
 */
App.projectModel = Em.Object.create({
    url:'projectdetail'
});

App.projectDetailController = Em.ObjectController.create({
    content: null,
    activePane: 'pictures',

    populate: function(slug){
        var controller = this;
        require(['app/data_source'], function(){
            App.dataSource.get('projectdetail/' + slug, {}, function(data) {
                controller.set('content', data);
            });
        })
    }
});


App.ProjectDetailView = Em.View.extend({
    contentBinding: 'App.projectDetailController',
    templateName:'project-detail',
    classNames: ['lightgreen', 'section']
});

App.ProjectStatsView = Em.View.extend({
    templateName:'project-stats'
});


/* 
 * Media Viewer 
 */

App.projectMediaViewerController = Em.ObjectController.create({
    contentBinding: 'App.projectDetailController',
    activePane: 'pictures',
});

App.ProjectMediaView = Em.View.extend({
    contentBinding: 'App.projectMediaViewerController',
    templateName:'project-media',
});

App.ProjectMediaPicturesView = Em.View.extend({
    contentBinding: 'App.projectMediaViewerController',
    templateName:'project-media-pictures'
});

App.ProjectMediaPlanView = Em.View.extend({
    contentBinding: 'App.projectMediaViewerController',
    templateName:'project-media-plan'
});

App.ProjectMediaVideosView = Em.View.extend({
    contentBinding: 'App.projectMediaViewerController',
    templateName:'project-media-videos'
});

// MediaViewer: panes with media come after this
App.ProjectMediaMapView = Em.View.extend({
    // Explicit call to App.projectDetailController.content
    // because it doesn't work with App.projectMediaViewerController
    //contentBinding: 'App.projectMediaViewerController',
    contentBinding: 'App.projectDetailController.content',
    templateName:'project-media-map',
    map: {},
    didInsertElement: function(){
        var view = this;
        // Delayed loading here so we're sure it's rendered
        // Otherwise gmap might cough
        Ember.run.later(function(){
          var project = view.get('content');
          this.map = new BlueMap('bigmap', {
              slug: project.slug,
              latitude: project.latitude,
              longitude: project.longitude
          }).showProjects(); 
        }, 1000)
    },
});

// Used as Mediaviewer panes
App.ProjectMediaPaneView = Em.View.extend({
    contentBinding: 'App.projectMediaViewerController',
    activePaneBinding: 'App.projectMediaViewerController.activePane',
    classNames: ['pane'],
    classNameBindings: ['active'], 
    active: function(){
        if (this.get('activePane') == this.get('value')) {
            return true;
        }
        return false;
    }.property('activePane'),
    tagName: 'div',
});


// Used for Mediaviewer buttons to switch panes
App.ProjectMediaButtonView = Em.View.extend({
    contentBinding: 'App.projectMediaViewerController',
    activePaneBinding: 'App.projectMediaViewerController.activePane',
    classNameBindings: ['active'], 
    tagName: 'button',
    active: function(){
        if (this.get('activePane') == this.get('value')) {
            return true;
        }
        return false;
    }.property('activePane'),
    classNameBindings: ['active'],
    click: function(){
        this.set('activePane', this.get('value'));
    }
});


