/*
 Models
 */

App.MyProjectPitch = DS.Model.extend({
    url: 'projects/manage/pitches',

    project: DS.belongsTo('App.MyProject'),

    // Basics
    title: DS.attr('string'),
    pitch: DS.attr('string'),
    theme: DS.attr('string'),
    tags: DS.hasMany('App.Tag'),
    description: DS.attr('string'),
    need: DS.attr('string'),

    validBasics: function(){
        if (this.get('title') &&  this.get('pitch') && this.get('description') &&
            this.get('theme') && this.get('tags.length') && this.get('need')){
            return true;
        }
        return false;
    }.property('title', 'pitch', 'theme', 'tags', 'description', 'theme', 'need'),


    // Location
    country: DS.attr('string'),
    latitude: DS.attr('number'),
    longitude: DS.attr('number'),

    validLocation: function(){
        if (this.get('country') &&  this.get('latitude') && this.get('longitude')){
            return true;
        }
        return false;
    }.property('country', 'latitude', 'longitude'),


    // Media
    image: DS.attr('string'),
    image_small: DS.attr('string'),
    image_square: DS.attr('string'),
    image_bg: DS.attr('string'),

    validMedia: function(){
        if (this.get('image')){
            return true;
        }
        return false;
    }.property('image'),


    // Submitting
    status: DS.attr('string'),
    agreed: DS.attr('boolean'),

    created: DS.attr('date')
});



App.MyProjectPlan = DS.Model.extend({
    url: 'projects/manage/plans',

    project: DS.belongsTo('App.MyProject'),

    // Basics
    title: DS.attr('string'),
    pitch: DS.attr('string'),
    theme: DS.attr('string'),
    need: DS.attr('string'),
    tags: DS.hasMany('App.Tag'),

    validBasics: function(){
        if (this.get('title') &&  this.get('pitch') && this.get('theme') && this.get('need') && this.get('tags.length')){
            return true;
        }
        return false;
    }.property('title', 'pitch', 'theme', 'tags', 'slug'),

    // Description
    description: DS.attr('string'),
    effects: DS.attr('string'),
    future: DS.attr('string'),
    for_who: DS.attr('string'),
    reach: DS.attr('number'),

    validDescription: function(){
        if (this.get('description') &&  this.get('effects') && this.get('future') && this.get('for_who') && this.get('reach')){
            return true;
        }
        return false;
    }.property('description', 'effects', 'future', 'for_who', 'reach'),


    // Location
    country: DS.attr('string'),
    latitude: DS.attr('number'),
    longitude: DS.attr('number'),

    validLocation: function(){
        if (this.get('country') &&  this.get('latitude') && this.get('longitude')){
            return true;
        }
        return false;
    }.property('country', 'latitude', 'longitude'),


    // Media
    image: DS.attr('string'),
    image_small: DS.attr('string'),
    image_square: DS.attr('string'),
    image_bg: DS.attr('string'),

    validMedia: function(){
        if (this.get('image')){
            return true;
        }
        return false;
    }.property('image'),

    // Submitting
    status: DS.attr('string'),
    agreed: DS.attr('boolean'),

    created: DS.attr('date')
});


App.MyProject = DS.Model.extend({
    url: 'projects/manage',

    // Model fields
    slug: DS.attr('string'),
    title: DS.attr('string'),
    phase: DS.attr('string'),

    pitch: DS.belongsTo('App.MyProjectPitch'),
    plan: DS.belongsTo('App.MyProjectPlan'),

    isPhasePitch: function(){
        return this.get('phase') == 'pitch';
    }.property('phase'),
    isPhasePlan: function(){
        return this.get('phase') == 'plan';
    }.property('phase')
});





/*
 Controllers
 */


App.MyProjectController = Em.ObjectController.extend({
    needs: ['currentUser']
});

App.MyProjectPitchController = Em.ObjectController.extend(App.Editable, {
    needs: ['currentUser']

});

App.MyProjectPitchBasicsController = Em.ObjectController.extend(App.Editable, {});
App.MyProjectPitchLocationController = Em.ObjectController.extend(App.Editable, {});
App.MyProjectPitchDescriptionController = Em.ObjectController.extend(App.Editable, {});

App.MyProjectPitchSubmitController = Em.ObjectController.extend(App.Editable, {
    submitPitch: function(e){
        var controller = this;
        var model = this.get('model');
        model.set('status', 'submitted');
        model.on('didUpdate', function(){
            controller.transitionToRoute('myProjectPitchReview');
        });
        this.updateRecordOnServer();
    },
    exit: function(){
        this.set('model.status', 'new');
        this._super();
    }
});

App.MyProjectPitchReviewController = Em.ObjectController.extend({});


App.MyProjectPlanController = Em.ObjectController.extend(App.Editable, {
    needs: ['currentUser']

});

App.MyProjectPlanBasicsController = Em.ObjectController.extend(App.Editable, {});
App.MyProjectPlanDescriptionController = Em.ObjectController.extend(App.Editable, {});
App.MyProjectPlanLocationController = Em.ObjectController.extend(App.Editable, {});
App.MyProjectPlanMediaController = Em.ObjectController.extend(App.Editable, {});
App.MyProjectPlanSubmitController = Em.ObjectController.extend(App.Editable, {});


/*
 Views
 */


App.MyProjectListView = Em.View.extend({
    templateName: 'my_project_list'

});

App.MyProjectView = Em.View.extend({
    templateName: 'my_project'

});


// Project Pitch Phase

App.MyProjectPitchView = Em.View.extend({
    templateName: 'my_project_pitch'

});

App.MyProjectPitchIndexView = Em.View.extend({
    templateName: 'my_pitch_index'

});

App.MyProjectPitchBasicsView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_pitch_basics'
});

App.MyProjectPitchDescriptionView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_pitch_description'
});

App.MyProjectPitchLocationView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_location'
});


App.MyProjectPitchSubmitView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_pitch_submit'
});



// Project Plan phase

App.MyProjectPlanView = Em.View.extend({
    templateName: 'my_project_plan'

});


App.MyProjectPlanIndexView = Em.View.extend({
    templateName: 'my_project_plan_index'

});

App.MyProjectPlanBasicsView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_basics'
});

App.MyProjectPlanDescriptionView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_description'
});

App.MyProjectPlanLocationView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_location'
});

