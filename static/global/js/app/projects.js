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
    organization: DS.attr('string'),
    description: DS.attr('string'),
    money_asked: DS.attr('number'),
    money_donated: DS.attr('number'),
    tags: DS.attr('array'),
    owner: DS.belongsTo('App.Member', {embedded: true}),
    country: DS.belongsTo('App.Country', {embedded: true}),
   // For now we set some default values here because we don't have actual numbers
    supporter_count: DS.attr('number', {defaultValue: 777}),
    days_left: DS.attr('number', {defaultValue: 777}),


    // For now we do some html generating here.
    // TODO: solve this in Ember or Handlebars helper
    days_left_span: function(){
        var dl = this.get('days_left').toString();
        var html = '';
        for (var i = 0, len = dl.length; i < len; i += 1) {
            html += '<span>' + dl.charAt(i) + '</span>'
        }
        return html;
    }.property('days_left'),

    supporter_count_span: function(){
        var dl = this.get('supporter_count').toString();
        var html = '';
        for (var i = 0, len = dl.length; i < len; i += 1) {
            html += '<span>' + dl.charAt(i) + '</span>'
        }
        return html;
    }.property('supporter_count')
    
    
})

App.projectSearchController = App.ListController.create({
    model: App.Project,
});

/* The search results. */
App.ProjectSearchView  = Em.View.extend({
    countBinding: 'App.projectSearchController.count',
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
    contentBinding: "App.projectDetailController",
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


App.ProjectTagsView = Em.CollectionView.extend({
    limit: 4,
    contentBinding: "App.projectDetailController.content.tags",
    tagName: 'ul',
    classNames: ['project-tags'],
    emptyView: Em.View.extend({
      template: function(){ return '<li class="none">none</li>';}
    }),
    itemViewClass: 'App.ProjectTagItemView',
});


App.ProjectTagItemView = Em.View.extend({
    tagName: 'li',
    limitBinding: 'parentView.limit',
    classNameBindings: ['outOfRange'],
    outOfRange: function(){
        if(this.get('contentIndex') > this.get('limit')){
             return 'out-of-range';
        }
    }.property('contentIndex'),
    templateName: 'project_tag_item',
    templateFile: 'project_detail'
});

App.ProjectTagsMoreView = Em.View.extend({
    limit: 4,
    contentBinding: "App.projectDetailController.content.tags",
    more: function(){
        if (this.get('content') == undefined) {
            return 0;
        }
        return this.get('content').length - this.get('limit');
    }.property('limit', 'content'),
    classNameBindings: ['outOfRange'],
    outOfRange: function(){
        if (this.get('content') == undefined) {
            return 'hidden';
        }
        if(this.get('content').length <= this.get('limit')){
             return 'hidden';
        }
    }.property('content'),
    tagName: 'span',
    templateName: 'project_tags_more',
    templateFile: 'project_detail'
});


