App.Country = DS.Model.extend({
    name: DS.attr('string'),
    subregion: DS.attr('string'),
})


App.Project = DS.Model.extend({
    url: 'projects',
    slug: DS.attr('string'),
    title: DS.attr('string'),
    image: DS.attr('string'),
    phase: DS.attr('string'),
    description: DS.attr('string'),
    money_asked: DS.attr('number'),
    money_donated: DS.attr('number'),
    tags: DS.attr('array'),
    owner: DS.belongsTo('App.Member', {embedded: true}),
    country: DS.belongsTo('App.Country', {embedded: true}),
})

App.projectSearchController = App.ListController.create({
    content: [],
    model: App.Project,
});

/* The search results. */
App.ProjectSearchView  = Em.View.extend({
    tagName: 'div',
    templateName: 'project_search',
    classNames: ['container'],

});

App.ProjectSearchResultsView = Em.CollectionView.extend({
    contentBinding: "App.projectSearchController",
    tagName: 'ul',
    emptyView: Em.View.extend({
      templateName: 'project_no_results',
      templateFile: 'project_search'
    }),
    itemViewClass: 'App.ProjectPreviewView',


});


App.ProjectPreviewView = Em.View.extend({
    tagName: 'li',
    templateName: 'project_preview',
    templateFile: 'project_search'
});

App.ProjectSupportersView = Em.View.extend({
    tagName: 'div',
    templateName: 'project_supporters',
    templateFile: 'project_detail'
});


App.projectDetailController = App.DetailController.create({
    model: App.Project
});


App.ProjectDetailView = Em.View.extend({
    contentBinding: 'App.projectDetailController',
    templateName: 'project_detail',
    classNames: ['lightgreen', 'section'],
});
