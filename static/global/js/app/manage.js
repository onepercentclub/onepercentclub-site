/*
 Models
 */

App.MyProjectPitch = DS.Model.extend({

    plan: DS.belongsTo('App.MyProject'),

    // Basics
    title: DS.attr('string'),
    pitch: DS.attr('string'),
    theme: DS.attr('string'),
    slug: DS.attr('string'),
    tags: DS.hasMany('App.Tag'),

    // Description
    description: DS.attr('string'),
    effects: DS.attr('string'),
    future: DS.attr('string'),
    for_who: DS.attr('string'),
    reach: DS.attr('number'),

    // Location
    country: DS.belongsTo('App.ProjectCountry'),
    latitude: DS.attr('number'),
    longitude: DS.attr('number'),

    // Media
    image: DS.attr('string'),
    image_small: DS.attr('string'),
    image_square: DS.attr('string'),
    image_bg: DS.attr('string'),

    created: DS.attr('date')
});


App.MyProjectPlan = App.MyProjectPitch.extend({

});

App.MyProject = DS.Model.extend({
    url: 'projects/manage',

    // Model fields
    slug: DS.attr('string'),
    title: DS.attr('string'),
    phase: DS.attr('string'),

    pitch: DS.belongsTo('App.MyProjectPitch'),
    plan: DS.belongsTo('App.MyProjectPlan'),

    isPitch: function(){
        return this.get('phase') == 'pitch';
    }.property('phase'),
    isPitch: function(){
        return this.get('phase') == 'pitch';
    }.property('phase')
});





/*
 Controllers
 */


App.MyPitchController = Em.ObjectController.extend({
    needs: ['currentUser']

});

App.MyProjectController = Em.ObjectController.extend({
    needs: ['currentUser']


});


/*
 Views
 */


// Project Pitch Phase

App.MyPitchView = Em.View.extend({
    templateName: 'my_pitch'

});


App.MyPitchIndexView = Em.View.extend({
    templateName: 'my_project_index'

});

App.MyPitchBasicsView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_basics'
});

App.MyPitchDescriptionView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_description'
});

App.MyPitchLocationView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_location'
});




// Project Plan phase

App.MyProjectListView = Em.View.extend({
    templateName: 'my_project_list'

});

App.MyProjectView = Em.View.extend({
    templateName: 'my_project'

});


App.MyProjectIndexView = Em.View.extend({
    templateName: 'my_project_index'

});

App.MyProjectBasicsView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_basics'
});

App.MyProjectDescriptionView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_description'
});

App.MyProjectLocationView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_location'
});

