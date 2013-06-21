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
    type: DS.attr('string', {defaultValue: 'physical'}),

    validAddress: function(){
        if (this.get('line1') &&  this.get('city') && this.get('country')){
            return true;
        }
        return false;
    }.property('line1', 'city', 'country')

});

App.MyOrganizationDocument = DS.Model.extend({
    url: 'organizations/documents/manage',

    organization: DS.belongsTo('App.MyOrganization'),
    file: DS.attr('file')
});

App.MyProjectAmbassador = DS.Model.extend({
    url: 'projects/ambassadors/manage',

    project_plan: DS.belongsTo('App.MyProjectPlan'),
    name: DS.attr('string'),
    email: DS.attr('string'),
    description: DS.attr('string')
});

App.MyProjectBudgetLine = DS.Model.extend({
    url: 'projects/budgetlines/manage',

    project_plan: DS.belongsTo('App.MyProjectPlan'),
    description: DS.attr('string'),
    amount: DS.attr('number')
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

    validProfile: function(){
        if (this.get('name') &&  this.get('description') && this.get('email') && this.get('addresses.firstObject.validAddress')){
            return true;
        }
        return false;
    }.property('name', 'description', 'email', 'addresses.firstObject.validAddress'),


    // Legal
    legalStatus: DS.attr('string'),
    documents: DS.hasMany('App.MyOrganizationDocument'),

    validLegalStatus: function(){
        if (this.get('legalStatus') &&  this.get('documents.length') > 0){
            return true;
        }
        return false;
    }.property('legalStatus', 'documents.length'),

    // Bank
    account_bank_name: DS.attr('string'),
    account_bank_address: DS.attr('string'),
    account_bank_country: DS.attr('string'),
    account_iban: DS.attr('string'),
    account_bic: DS.attr('string'),
    account_number: DS.attr('string'),
    account_name: DS.attr('string'),
    account_city: DS.attr('string'),
    account_other: DS.attr('string'),

    validBank: function(){
        if (this.get('account_bank_name') &&  this.get('account_bank_country') && this.get('account_name') && this.get('account_city') && (this.get('account_number') || this.get('account_iban'))){
            return true;
        }
        return false;
    }.property('account_bank_name', 'account_bank_country', 'account_name', 'account_city', 'account_iban', 'account_number')

});


App.MyProjectPitch = DS.Model.extend({
    url: 'projects/pitches/manage',

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
    image: DS.attr('image'),

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
    url: 'projects/plans/manage',

    project: DS.belongsTo('App.MyProject'),

    // Basics
    title: DS.attr('string'),
    pitch: DS.attr('string'),
    theme: DS.attr('string'),
    need: DS.attr('string'),
    tags: DS.hasMany('App.Tag'),


    needsFunding: function (){
        if (this.get('need') == 'finance' || this.get('need') == 'both') {
            return true;
        }
        return false;
    }.property('need'),

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
    forWho: DS.attr('string'),
    reach: DS.attr('number'),

    validDescription: function(){
        if (this.get('description') &&  this.get('effects') && this.get('future') && this.get('forWho') && this.get('reach')){
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
    image: DS.attr('image'),

    validMedia: function(){
        if (this.get('image')){
            return true;
        }
        return false;
    }.property('image'),

    // Organization
    organization: DS.belongsTo('App.MyOrganization'),

    // Ambassadors
    ambassadors: DS.hasMany('App.MyProjectAmbassador'),

    validAmbassadors: function(){
        if (this.get('ambassadors.length') > 2) {
            return true;
        }
        return false;
    }.property('ambassadors.length'),

    // Submitting
    status: DS.attr('string'),

    // Crowd funding
    moneyNeeded: DS.attr('string'),
    campaign: DS.attr('string'),

    validCampaign: function(){
        if (this.get('moneyNeeded') &&  this.get('campaign')){
            return true;
        }
        return false;
    }.property('moneyNeeded', 'campaign'),

    // Budget
    budgetLines: DS.hasMany('App.MyProjectBudgetLine'),

    totalBudget: function(){
        var lines = this.get('budgetLines');
        return lines.reduce(function(prev, line){
            return (prev || 0) + (line.get('amount')/1 || 0);
        });
    }.property('budgetLines.@each.amount'),

    validBudget: function(){
        if (this.get('totalBudget') > 0 &&  this.get('totalBudget') <= 5000 ){
            return true;
        }
        return false;
    }.property('totalBudget'),


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

    coach: DS.belongsTo('App.User'),

    isPhasePitch: function(){
        return this.get('phase') == 'pitch';
    }.property('phase'),
    isPhasePlan: function(){
        return this.get('phase') == 'plan';
    }.property('phase'),

    inProgress: function(){
        var phase = this.get('phase');
        if (phase == 'realized') {
            return false;
        }
        if (phase == 'closed') {
            return false;
        }
        return true;
    }.property('phase', 'pitch.status', 'plan.status')

});


/*
 Controllers
 */


App.MyProjectController = Em.ObjectController.extend({
    needs: ['currentUser']
});

App.MyPitchNewController = Em.ObjectController.extend(App.Editable, {
    needs: ['currentUser'],
    updateRecordOnServer: function(){
        var controller = this;
        var model = this.get('model');
        model.one('becameInvalid', function(record){
            model.set('errors', record.get('errors'));
        });

        model.one('didCreate', function(record){
            controller.transitionToRoute('myProjectPitch', record);
        });

        model.transaction.commit();
    },
});



App.MyProjectListController = Em.ArrayController.extend({
    needs: ['currentUser'],
    canPitchNew: function(){
        var can = true;
        this.get('model').forEach(function(project){
            if (project.get('inProgress')) {
                can = false;
            }
        });
        return can;
    }.property('model.@each.phase')

});

App.MyProjectPitchController = Em.ObjectController.extend(App.Editable, {
    needs: ['currentUser']

});

App.MyProjectPitchBasicsController = Em.ObjectController.extend(App.Editable, {});
App.MyProjectPitchLocationController = Em.ObjectController.extend(App.Editable, {});
App.MyProjectPitchMediaController = Em.ObjectController.extend(App.Editable, {
    addFile: function(file) {
        var model = this.get('model');
        model.set('image', file);
        this.set('imageSelected', true);
        model.on('didUpdate', function(){
            this.set('imageSelected', false);
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
App.MyProjectPlanMediaController = Em.ObjectController.extend(App.Editable, {});
App.MyProjectPlanCampaignController = Em.ObjectController.extend(App.Editable, {});

App.MyProjectPlanAmbassadorsController = Em.ObjectController.extend(App.Editable, {
    shouldSave: function(){
        // Determine if any part is dirty, project plan or any of the ambassadors
        if (this.get('isDirty')) {
            return true;
        }
        var ambassadors = this.get('ambassadors');
        var dirty = false;
        ambassadors.forEach(function(ad){
             if (ad.get('isDirty')) {
                 dirty = true;
             }

        });
        return dirty;
    }.property('isDirty', 'ambassadors.@each.isDirty'),

    addAmbassador: function(){
        // Use the same transaction as the projectplan
        var transaction =  this.get('model').transaction;
        var ambassador = transaction.createRecord(App.MyProjectAmbassador, {});
        this.get('ambassadors').pushObject(ambassador);
    },

    removeAmbassador: function(ambassador){
        ambassador.deleteRecord();
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



App.MyProjectPlanBankController = Em.ObjectController.extend(App.Editable, {

    shouldSave: function(){
        // Determine if any part is dirty, project plan, org or any of the org addresses
        if (this.get('isDirty')) {
            return true;
        }
        if (this.get('organization.isDirty')) {
            return true;
        }
        return false;
    }.property('organization.isLoaded', 'isDirty')
});



App.MyProjectPlanBudgetController = Em.ObjectController.extend(App.Editable, {

    shouldSave: function(){
        // Determine if any part is dirty, project plan or any of the budget_lines
        if (this.get('isDirty')) {
            return true;
        }
        var budgetLines = this.get('budgetLines');
        var dirty = false;
        budgetLines.forEach(function(line){
             if (line.get('isDirty')) {
                 dirty = true;
             }

        });
        return dirty;
    }.property('isDirty', 'budgetLines.@each.isDirty'),

    addBudgetLine: function(){
        // Use the same transaction as the projectplan
        var transaction =  this.get('model').transaction;
        var line = transaction.createRecord(App.MyProjectBudgetLine, {});
        this.get('budgetLines').pushObject(line);
    },

    removeBudgetLine: function(line){
        line.deleteRecord();
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



App.MyProjectPlanSubmitController = Em.ObjectController.extend(App.Editable, {
    submitPlan: function(e){
        var controller = this;
        var model = this.get('model');
        model.set('status', 'submitted');
        model.on('didUpdate', function(){
            controller.transitionToRoute('myProjectPlanReview');
        });
        this.updateRecordOnServer();
    },
    exit: function(){
        this.set('model.status', 'new');
        this._super();
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

App.MyPitchNewView = Em.View.extend({
    templateName: 'my_pitch_new'

});

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

App.MyProjectPlanAmbassadorsView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_ambassadors'
});

App.MyProjectPlanBankView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_bank'
});

App.MyProjectPlanBudgetView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_budget'
});

App.MyProjectPlanCampaignView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_campaign'
});

App.MyProjectPlanSubmitView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_submit'
});


