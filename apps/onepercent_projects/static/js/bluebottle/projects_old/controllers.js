App.ProjectListController = Em.ArrayController.extend({
    needs: ['projectSearchForm']
});


App.ProjectSearchFormController = Em.ObjectController.extend({
    needs: ['projectList'],

    // Number of results to show on one page
    pageSize: 8,


    // Have a property for this so we can easily use another list controller if we extend this.
    listController: function(){
        return this.get('controllers.projectList');
    }.property(),

    init: function(){
        // Make sure this record is in it's own transaction so it will never pollute other commits.
        var transaction = this.get('store').transaction();
        var form =  transaction.createRecord(App.ProjectSearch);
        this.set('model', form);
        this.updateSearch();
    },

    rangeStart: function(){
        return this.get('page') * this.get('pageSize') - this.get('pageSize') + 1;
    }.property('listController.model.length'),

    rangeEnd: function(){
        return this.get('page') * this.get('pageSize') - this.get('pageSize') + this.get('listController.model.length');
    }.property('listController.model.length'),

    hasNextPage: function(){
        var next = this.get('page') * this.get('pageSize');
        var total = this.get('listController.model.meta.total');
        return (next < total);
    }.property('listController.model.meta.total'),

    hasPreviousPage: function(){
        return (this.get('page') > 1);
    }.property('page'),

    orderedByPopularity: function(){
        return (this.get('ordering') == 'popularity');
    }.property('ordering'),
    orderedByTitle: function(){
        return (this.get('ordering') == 'title');
    }.property('ordering'),
    orderedByNewest: function(){
        return (this.get('ordering') == 'newest');
    }.property('ordering'),
    orderedByNeeded: function(){
        return (this.get('ordering') == 'money_needed');
    }.property('ordering'),
    orderedByDeadline: function(){
        return (this.get('ordering') == 'deadline');
    }.property('ordering'),

    updateSearch: function(sender, key){
        if (key != 'page') {
            // If the query changes we should jump back to page 1
            this.set('page', 1);
        }
        if (this.get('model.isDirty') ) {
            var list = this.get('listController');
            var controller = this;

            var query = {
                'page_size': this.get('pageSize'),
                'page': this.get('page'),
                'ordering': this.get('ordering'),
                'phase': this.get('phase'),
                'country': this.get('country'),
                'text': this.get('text'),
                'theme': this.get('theme')
            };
            var projects = App.ProjectPreview.find(query);
            list.set('model', projects);
        }
    }.observes('text', 'country', 'theme', 'phase', 'page', 'ordering'),

    actions: {
        nextPage: function(){
            this.incrementProperty('page');
        },

        previousPage: function(){
            this.decrementProperty('page');
        },

        sortOrder: function(order) {
            this.set('ordering', order);
        },
        clearForm: function(sender, key) {
            this.set('model.text', '');
            this.set('model.country', null);
            this.set('model.theme', null);
            this.set('model.phase', null);
        }

    }
});


App.ProjectController = Em.ObjectController.extend({
    needs: ['projectIndex', 'currentUser'],

    isFundable: function(){
       return (this.get('phase') == 'campaign' && this.get('campaign.money_asked'));
    }.property('phase', 'campaign'),

    allTags: function() {
        var tags = this.get('plan.tags');
        return tags.reduce(function(previousValue, tag, index) {
            var separator = (index == 0 ? " " : ", ");
            return previousValue + separator + tag.id;
        }, "");
    }.property('tags.@each'),

    isProjectOwner: function() {
        var username = this.get('controllers.currentUser.username');
        var ownername = this.get('model.owner.username');
        if (username) {
            return (username == ownername);
        }
        return false;
    }.property('model.owner', 'controllers.currentUser.username')

});


App.ProjectSupporterListController = Em.ArrayController.extend({
    supportersLoaded: function(sender, key) {
        if (this.get(key)) {
            this.set('model', this.get('supporters').toArray());
        } else {
            // Don't show old content when new content is being retrieved.
            this.set('model', null);
        }
    }.observes('supporters.isLoaded')

});


App.ProjectIndexController = Em.ArrayController.extend({
    needs: ['project', 'currentUser'],
    perPage: 5,
    page: 1,

    remainingItemCount: function(){
        if (this.get('meta.total')) {
            return this.get('meta.total') - (this.get('page')  * this.get('perPage'));
        }
        return 0;
    }.property('page', 'perPage', 'meta.total'),

    canLoadMore: function(){
        var totalPages = Math.ceil(this.get('meta.total') / this.get('perPage'));
        return totalPages > this.get('page');
    }.property('perPage', 'page', 'meta.total'),

    actions: {
        showMore: function() {
            var controller = this;
            var page = this.incrementProperty('page');
            var id = this.get('controllers.project.model.id');
            App.WallPost.find({'parent_type': 'project', 'parent_id': id, page: page}).then(function(items){
                controller.get('model').pushObjects(items.toArray());
            });
        }
    },
    isProjectOwner: function() {
        var username = this.get('controllers.currentUser.username');
        var ownername = this.get('controllers.project.model.owner.username');
        if (username) {
            return (username == ownername);
        }
        return false;
    }.property('controllers.project.model.owner', 'controllers.currentUser.username')

});



/*
 Project Manage Controllers
 */


App.MyProjectController = Em.ObjectController.extend({
    needs: ['currentUser']
});

App.MyPitchNewController = Em.ObjectController.extend(App.Editable, {
    needs: ['currentUser'],
    actions: {
        updateRecordOnServer: function(){
            var controller = this;
            var model = this.get('model');
            model.one('becameInvalid', function(record){
                model.set('errors', record.get('errors'));
            });

            model.one('didCreate', function(record){
                controller.transitionToRoute('myProjectPitch', record);
            });

            model.save();
        }
    }
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

App.MyProjectPitchBasicsController = Em.ObjectController.extend(App.Editable, {
    nextStep: 'myProjectPitch.location'
});
App.MyProjectPitchLocationController = Em.ObjectController.extend(App.Editable, {
    nextStep: 'myProjectPitch.media'
});
App.MyProjectPitchMediaController = Em.ObjectController.extend(App.Editable, {
    nextStep: 'myProjectPitch.submit',

    actions: {
        save: function(record) {
            this._super();
            this.get('model').reload();
        }
    }
});

App.MyProjectPitchSubmitController = Em.ObjectController.extend(App.Editable, {
    actions: {
        submitPitch: function(e){
            var controller = this;
            var model = this.get('model');
            model.set('status', 'submitted');
            model.on('didUpdate', function(){
                controller.transitionToRoute('myProjectPitchReview');
            });
            model.save();
        }
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

App.MyProjectPlanBasicsController = Em.ObjectController.extend(App.Editable, {
    nextStep: 'myProjectPlan.description'
});
App.MyProjectPlanDescriptionController = Em.ObjectController.extend(App.Editable, {
    nextStep: 'myProjectPlan.location'
});
App.MyProjectPlanLocationController = Em.ObjectController.extend(App.Editable, {
    nextStep: 'myProjectPlan.media'
});
App.MyProjectPlanSubmitController = Em.ObjectController.extend(App.Editable, {});

App.MyProjectPlanMediaController = Em.ObjectController.extend(App.Editable, {
    nextStep: 'myProjectPlan.organisation'
});
App.MyProjectPlanCampaignController = Em.ObjectController.extend(App.Editable, {
    nextStep: 'myProjectPlan.budget'
});

/*
App.MyProjectPlanAmbassadorsController = Em.ObjectController.extend(App.Editable, {
    nextStep: function(){
        if (this.get('need') == 'skills') {
            return 'myProjectPlan.submit'
        } else {
            return 'myProjectPlan.campaign'
        }
    }.property('need'),

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

    actions: {
        updateRecordOnServer: function(){
            var controller = this;
            var model = this.get('model');
            model.transaction.commit();


            // The minimum number of ambassadors requirement was dropped, plus there was no visual feedback if not
            // enough ambassadors
            //if (model.get('validAmbassadors')) {
            controller.transitionToRoute(controller.get('nextStep'));
            //}

        },

        addAmbassador: function(){
            // Use the same transaction as the projectplan
            var transaction =  this.get('model').transaction;
            var ambassador = transaction.createRecord(App.MyProjectAmbassador, {});
            this.get('ambassadors').pushObject(ambassador);
        },

        removeAmbassador: function(ambassador){
            ambassador.deleteRecord();
        }
    }

});
*/

App.MyProjectPlanOrganisationController = Em.ObjectController.extend(App.Editable, {

    nextStep: 'myProjectPlan.legal',

    shouldSave: function(){
        // Determine if any part is dirty, project plan, org or any of the org addresses
        if (this.get('isDirty')) {
            return true;
        }
        if (this.get('organization.isDirty')) {
            return true;
        }
        return false;
    }.property('organization.isLoaded', 'organization.isDirty'),

    actions: {
        updateRecordOnServer: function(){
            var controller = this;
            var model = this.get('model');
            var organization = model.get('organization');

            organization.one('didUpdate', function(){
                // Updated organization info.
                controller.transitionToRoute(controller.get('nextStep'));
                $("html, body").animate({ scrollTop: 0 }, 600);
            });
            organization.one('didCreate', function(){
                // Create organization info.
                controller.transitionToRoute(controller.get('nextStep'));
                $("html, body").animate({ scrollTop: 0 }, 600);
            });
            model.transaction.commit();
        },
        selectOrganization: function(org){
            // Use the same transaction as the projectplan
            var transaction =  this.get('model').transaction;
            transaction.add(org);
            this.set('organization', org);
        },

        createNewOrganization: function() {
            var controller = this;
            var transaction = this.get('store').transaction();
            var org = transaction.createRecord(App.MyOrganization, {name: controller.get('model.title')});
            this.set('model.organization', org);
        }
    }
});



App.MyProjectPlanBankController = Em.ObjectController.extend(App.Editable, {

    nextStep: 'myProjectPlan.submit',

    shouldSave: function(){
        // Determine if any part is dirty, project plan, org or any of the org addresses
        if (this.get('isDirty')) {
            return true;
        }
        if (this.get('organization.isDirty')) {
            return true;
        }
        return false;
    }.property('organization.isLoaded', 'isDirty'),

    actions: {
        updateRecordOnServer: function(){
            var controller = this;
            var model = this.get('model.organization');
            model.one('becameInvalid', function(record){
                model.set('errors', record.get('errors'));
            });
            model.one('didUpdate', function(){
                controller.transitionToRoute(controller.get('nextStep'));
                window.scrollTo(0);
            });
            model.one('didCreate', function(){
                controller.transitionToRoute(controller.get('nextStep'));
                window.scrollTo(0);
            });

            model.save();
        }
    }
});



App.MyProjectPlanBudgetController = Em.ObjectController.extend(App.Editable, {

    nextStep: 'myProjectPlan.bank',

    shouldSave: function(){
        // Determine if any part is dirty, project plan or any of the budget_lines
        if (this.get('isDirty')) {
            return true;
        }
        var budgetLines = this.get('budgetLines');
        var dirty = false;
        budgetLines.forEach(function(ad){
             if (ad.get('isDirty')) {
                 dirty = true;
             }

        });
        return dirty;
    }.property('isDirty', 'budgetLines.@each.isDirty'),

    // only show the budget errors if no budget was entered on the first display
    showBudgetError: function(){
        var validBudget = this.get('validBudget');
        var totalBudget = this.get('totalBudget');
        return (totalBudget && !validBudget);
    }.property('validBudget', 'totalBudget'),

    actions: {
        updateRecordOnServer: function(){
            var controller = this;
            var model = this.get('model');
            model.transaction.commit();
            if (model.get('validBudget')) {
                controller.transitionToRoute(controller.get('nextStep'));
            }
        },

        addBudgetLine: function(){
            // Use the same transaction as the projectplan
            var transaction =  this.get('model').transaction;
            var line = transaction.createRecord(App.MyProjectBudgetLine, {});
            this.get('budgetLines').pushObject(line);
        },

        removeBudgetLine: function(line){
            line.deleteRecord();
        }
    }

});


App.MyProjectPlanLegalController = Em.ObjectController.extend(App.Editable, {

    /*nextStep: 'myProjectPlan.ambassadors', */
    nextStep: 'myProjectPlan.campaign',

    shouldSave: function(){
        // Determine if any part is dirty, project plan, org or any of the org addresses
        if (this.get('isDirty')) {
            return true;
        }
        if (this.get('organization.isDirty')) {
            return true;
        }
    }.property('organization.isLoaded'),

    actions: {
        updateRecordOnServer: function() {
            var controller = this;
            var model = this.get('model.organization');
            model.one('becameInvalid', function(record){
                model.set('errors', record.get('errors'));
            });
            model.one('didUpdate', function(){
                controller.transitionToRoute(controller.get('nextStep'));
                window.scrollTo(0);
            });
            model.one('didCreate', function(){
                controller.transitionToRoute(controller.get('nextStep'));
                window.scrollTo(0);
            });

            model.save();
        },

        removeFile: function(doc) {
            var transaction = this.get('model').transaction;
            transaction.add(doc);
            doc.deleteRecord();
            transaction.commit();
        }
    },

    addFile: function(file) {
        var store = this.get('store');
        var doc = store.createRecord(App.MyOrganizationDocument);
        doc.set('file', file);
        var org = this.get('organization');
        doc.set('organization', org);
        doc.save();
    }
});



App.MyProjectPlanSubmitController = Em.ObjectController.extend(App.Editable, {

    actions: {
        submitPlan: function(e){
            var controller = this;
            var model = this.get('model');
            model.set('status', 'submitted');
            model.on('didUpdate', function(){
                controller.transitionToRoute('myProjectPlanReview');
            });
            model.save();
        }
    },

    exit: function(){
        this.set('model.status', 'new');
        this._super();
    }
});

App.MyProjectCampaignController = Em.ObjectController.extend({
    project: function() {
        return this.get('model');
    }.property('model')
});
