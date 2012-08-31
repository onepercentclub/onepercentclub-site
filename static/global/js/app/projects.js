/*
 * Project Search and List
 */
// FIXME: We're not using this Model right now.
App.ProjectPreviewModel = Em.Object.extend({
});


App.projectSearchController = Em.ArrayController.create({
    // The saved query state.
    query: {},

    // Project preview search results.
    searchResults: null,

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

    populate: function() {
        var controller = this;
        require(['app/data_source'], function(){
            var query = controller.get('query');

            // Get the project preview data using the current query.
            // We're limiting the number of returned items to 4.
            var projectPreviewQuery = $.extend({limit: 4}, query);
            App.dataSource.get('projectpreview', projectPreviewQuery, function(data) {
                controller.set('searchResults', data['objects']);
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
        console.log(selectedCountry);
        if (selectedCountry != null && selectedCountry['id'].length > 0) {
            query.countries = selectedCountry['id'];
        } else {
            delete query.countries;
        }

        // Set the query and re-populate the data.
        this.set('query', query)
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
        App.projectSearchController.update();
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
//
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
