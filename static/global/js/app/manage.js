/*
 Models
 */

App.AddressTypeSelectView = Em.Select.extend({
    content: [
        {value: 'physical', title: "Physical"},
        {value: 'postal', title: "Postal"},
        {value: 'other', title: "Other"}
    ],
    optionValuePath: "content.value",
    optionLabelPath: "content.title"
});


App.MyOrganizationAddress = DS.Model.extend({
    url: 'organizations/addresses/manage',

    organization: DS.belongsTo('App.MyOrganization'),
    line1: DS.attr('string'),
    line2: DS.attr('string', {defaultValue: ''}),
    postal_code: DS.attr('string'),
    city: DS.attr('string'),
    country: DS.attr('string'),
    type: DS.attr('string', {defaultValue: 'physical'})

});

App.MyOrganizationDocument = DS.Model.extend({
    url: 'organizations/documents/manage',

    organization: DS.belongsTo('App.MyOrganization'),
    file: DS.attr('file')
});

App.MyOrganization = DS.Model.extend({
    url: 'organizations/manage',
    name: DS.attr('string'),
    description: DS.attr('string'),

    // Internet
    website: DS.attr('string'),
    email: DS.attr('string'),
    facebook: DS.attr('string'),
    twitter: DS.attr('string'),
    skype: DS.attr('string'),

    // Addresses
    addresses: DS.hasMany('App.MyOrganizationAddress'),

    // Legal
    legal_status: DS.attr('string'),
    documents: DS.hasMany('App.MyOrganizationDocument'),
    registration: DS.attr('string')
});


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

    // Organization
    organization: DS.belongsTo('App.MyOrganization'),

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
App.MyProjectPitchMediaController = Em.ObjectController.extend(App.Editable, {
    addFile: function(file) {
        var model = this.get('model');
        model.set('file', file);
        model.on('didUpdate', function(){
            model.set('file', null);
        });
    }

});

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
App.MyProjectPlanSubmitController = Em.ObjectController.extend(App.Editable, {});

App.MyProjectPlanMediaController = Em.ObjectController.extend(App.Editable, {
    addFile: function(file) {
        this.set('model.file', file);
    }
});


App.MyProjectPlanOrganisationController = Em.ObjectController.extend(App.Editable, {

    shouldSave: function(){
        // Determine if any part is dirty, project plan, org or any of the org addresses
        if (this.get('isDirty')) {
            return true;
        }
        if (this.get('organization.isDirty')) {
            return true;
        }
        var addresses = this.get('organization.addresses');
        var dirty = false;
        addresses.forEach(function(ad){
             if (ad.get('isDirty')) {
                 dirty = true;
             }

        });
        return dirty;
    }.property('organization.isLoaded', 'organization.addresses.@each.isDirty'),

    addAddress: function(){
        // Use the same transaction as the projectplan
        var transaction =  this.get('model').transaction;
        var address = transaction.createRecord(App.MyOrganizationAddress, {});
        this.get('model.organization.addresses').pushObject(address);
    },

    removeAddress: function(address){
        address.deleteRecord();
    },


    selectOrganization: function(org){
        // Use the same transaction as the projectplan
        var transaction =  this.get('model').transaction;
        transaction.add(org);
        this.set('model.organization', org);
        if (this.get('model.organization.addresses.length') == 0) {
            this.addAddress();
        }
    },
    createNewOrganization: function() {
        // Use the same transaction as the projectplan
        var transaction =  this.get('model').transaction;
        var org = transaction.createRecord(App.MyOrganization, {});
        this.set('model.organization', org);
        this.addAddress();
    }
});


App.MyProjectPlanLegalController = Em.ObjectController.extend(App.Editable, {

    shouldSave: function(){
        // Determine if any part is dirty, project plan, org or any of the org addresses
        if (this.get('isDirty')) {
            return true;
        }
        if (this.get('organization.isDirty')) {
            return true;
        }
    }.property('organization.isLoaded'),

    addFile: function(file) {
        var transaction = this.get('model').transaction;
        var doc = transaction.createRecord(App.MyOrganizationDocument);
        doc.set('file', file);
        doc.set('organization',  this.get('organization'));
        doc.one('didCreate', function(record){
            this.get('organization').reload();
        });

        transaction.commit();
    },

    removeFile: function(doc) {
        var transaction = this.get('model').transaction;
        transaction.add(doc);
        doc.deleteRecord();
        transaction.commit();
    }

});



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

App.MyProjectPitchMediaView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_media'
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

App.MyProjectPlanMediaView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_media'
});

App.MyProjectPlanOrganisationView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_organisation'
});

App.MyProjectPlanLegalView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_legal'
});


