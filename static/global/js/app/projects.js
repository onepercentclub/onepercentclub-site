/*
 * Project Search and List
 */
// FIXME: We're not using this Model right now.
App.ProjectPreviewModel = Em.Object.extend({
});

App.ProjectModel = Em.Object.extend({
});


App.projectSearchController = Em.ArrayController.create({
    init: function() {
        this._super();
        this.populate();
    },

    // The saved queryFilter state.
    queryFilter: {},

    // Project preview search results and meta data from tastypie:
    content: null,
    contentMeta: [],

    // List of regions and countries returned from the search form filter. These
    // hold the information that will be presented in the UI.
    filteredRegions: [],
    filteredCountries: [],


    // Query filters that react after a button click or enter from the keyboard:
    searchText: "",
    submitTextSearchForm: function(event) {
        var searchText = this.get('searchText');
        this.updateQueryFilter({'text': searchText});
        this.populate();
    },

    // Query filters that react immediately to user input:
    selectedRegion: null,
    selectedRegionChanged: function() {
        var selectedRegion = this.get('selectedRegion');
        this.updateQueryFilter({'regions': selectedRegion['id']});
        this.populate()
    }.observes('selectedRegion'),

    selectedCountry: null,
    selectedCountryChanged: function() {
        var selectedCountry = this.get('selectedCountry');
        this.updateQueryFilter({'countries': selectedCountry['id']});
        this.populate()
    }.observes('selectedCountry'),


    // Pagination:
    nextSearchResult: function() {
        var meta  = this.get('contentMeta');
        var next = (RegExp('offset=' + '(.+?)(&|$)').exec(meta.next)||[,null])[1]
        return next;
    }.property('contentMeta'),
    
    previousSearchResult: function() {
        var meta  = this.get('contentMeta');
        var previous = (RegExp('offset=' + '(.+?)(&|$)').exec(meta.previous)||[,null])[1]
        return previous;
    }.property('contentMeta'),

    // We can't use an observer for this because it will loop continually.
    clickPrevNext: function(event, offset) {
        this.updateQueryFilter({'offset': offset});
        this.populate();
    },

    // Loads the data from the server based on the current value of queryFilter.
    populate: function() {
        var controller = this;
        require(['app/data_source'], function(){
            var query = controller.get('queryFilter');

            // Get the project preview data using the current queryFilter.
            // We're limiting the number of returned items to 4.
            var projectPreviewQuery = $.extend({limit: 4}, query);
            App.dataSource.get('projectpreview', projectPreviewQuery, function(data) {
                controller.set('content', data['objects']);
                controller.set('contentMeta', data['meta']);
            });

            // Get the project search data using the same queryFilter.
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

    // Updates the queryFilter based on the queryParam. Parameters  with a null
    // or empty value are removed from the filter list.
    updateQueryFilter: function(queryParam) {
        var query = this.get('queryFilter');
        var tempQuery = $.extend({}, query);

        // Delete the param if it's already in the queryFilter. This lets us update
        // the param or leave it deleted depending on what's requested.
        var i = 0;
        for (var property in queryParam) {
            if (i > 0) {
                // TODO: Support multiple queryFilter parameter updates.
                break;  // Only use the first property in queryParam.
            }
            if (undefined != tempQuery[property]) {
                delete tempQuery[property];
            }
            i++;
        }

        // The offset parameter needs to be deleted on every filter update.
        if (undefined != tempQuery['offset']) {
            delete tempQuery['offset'];
        }

        // Create an updated queryFilter.
        if (queryParam[property] == null || queryParam[property].length == 0 ) {
            // QueryParam[property] is null or empty string. Ignore it.
            var updatedQuery = tempQuery;
        } else {
            var updatedQuery = $.extend(queryParam, tempQuery);
        }

        // Set the updated queryFilter and populate the data.
        this.set('queryFilter', updatedQuery);
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
        App.projectSearchController.submitTextSearchForm(event);
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

    contentBinding: 'App.projectSearchController.content',
    itemViewClass: 'App.ProjectPreviewView'
});

App.ProjectPreviewView = Em.View.extend({
    tagName: 'li',
    templateName: 'project-preview',
    classNames: ['project-mid', 'grid_1', 'column']
});




/*
 * Project Detail
 */
App.projectModel = Em.Object.create({
    url:'projectdetail'
});

App.projectDetailController = Em.ObjectController.create({
    content: null,

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
    contentBinding: 'App.projectDetailController.content',
    templateName:'project-detail',
    classNames: ['lightgreen', 'section']
});

App.ProjectStatsView = Em.View.extend({
    templateName:'project-stats'
});

App.ProjectMediaView = Em.View.extend({
    contentBinding: 'App.projectDetailController.content',
    templateName:'project-media'
});

App.ProjectMediaPicturesView = Em.View.extend({
    templateName:'project-media-pictures'
});

App.ProjectMediaPlanView = Em.View.extend({
    templateName:'project-media-plan'
});

App.ProjectMediaVideosView = Em.View.extend({
    templateName:'project-media-videos'
});

App.ProjectMediaMapView = Em.View.extend({
    templateName:'project-media-map'
});


App.ProjectStartView = Em.View.extend({
    templateName:'project-start'
});

