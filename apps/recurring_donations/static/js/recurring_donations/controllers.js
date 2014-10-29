App.MonthlyDonationController = Em.ObjectController.extend({

    addressComplete: function(){
        if (this.get('profile.didError')) {
            return false;
        }
        if (this.get('profile.isDirty')) {
            return false;
        }
        return (this.get('profile.address.line1') && this.get('profile.address.city') && this.get('profile.address.country') && this.get('profile.address.postal_code'));
    }.property('profile.address.line1', 'profile.address.city', 'profile.address.country', 'profile.address.postal_code'),

    shouldSave: function(obj, keyName){
        var dirty = false;
        this.get('model.projects').forEach(function(record){
            if (record.get('isDirty')){
                dirty = true;
            }
        });
        if (this.get('model.isDirty')) {
            dirty = true;
        }
        return dirty;
    }.property('model.isDirty', 'model.projects.@each.isDirty'),

    startEditing: function() {
        var record = this.get('model');
        if (record.get('transaction.isDefault') == true) {
            this.transaction = this.get('store').transaction();
            this.transaction.add(record);
        }
    },

    stopEditing: function(){
        var self = this;
        var record = this.get('model');
        var transaction = record.get('transaction');
        var address = this.get('address');

        if (this.get('shouldSave')) {
            Bootstrap.ModalPane.popup({
                classNames: ['modal'],
                heading: gettext('Save changed data?'),
                message: gettext('You have some unsaved changes. Do you want to save before you leave?'),
                primary: gettext('Save'),
                secondary: gettext('Cancel'),
                callback: function(opts, e) {
                    e.preventDefault();
                    if (opts.primary) {
                        transaction.commit();
                        address.save();
                    }
                    if (opts.secondary) {
                        transaction.rollback();
                        address.rollback();
                    }
                }
            });
        }
    },
    actions: {
        openProjectSelectModal: function() {
            var route = this;
            $('#project-select').addClass('modal-active').removeClass('is-hidden');
            $('body').append('<div class="modal-backdrop"></div>');
            $('.modal-backdrop').click(function(){
                route.send('closeAllModals');
            });
        },

        closeAllModals: function(){
            $('.modal-active').removeClass('modal-active').addClass('is-hidden');
            $('.modal-backdrop').fadeOut(200, function(){
                this.remove();
            });
        },
        save: function(){
            var model = this.get('model');
            var message = gettext("You're about to set a monthly donation.<br/><br/>") +
                gettext("Has anybody ever told you that you're awesome? Well, you're awesome!<br/><br/>") +
                gettext("1%Club will withdraw your monthly donation from your bank account in the beginning of each month. You can cancel it anytime you like.<br/><br/>") +
                gettext("We will send you an email in the beginning of each month to update you on what projects received your support!");

            Bootstrap.ModalPane.popup({
                classNames: ['modal'],
                heading: gettext('Set my monthly donation'),
                message: message,
                primary: gettext('Save'),
                secondary: gettext('Cancel'),
                callback: function(opts, e) {
                    e.preventDefault();

                    if (opts.primary) {
                        model.save();
                        model.get('projects').forEach(function(project){
                            project.save();
                        });
                    }

                    if (opts.secondary) {
                        // Do nothing
                    }
                }
            });

        },
        toggleActive: function(sender, value){
            if (this.get('active')) {
                var model = this.get('model');
                Bootstrap.ModalPane.popup({
                    classNames: ['modal'],
                    heading: gettext('Stop my monthly donation'),
                    message: gettext('Thanks a lot for your support until now. You rock! We welcome you back anytime.<br /><br />Are you sure you want to stop your monthly support?'),
                    primary: gettext('Yes, stop my donation'),
                    secondary: gettext('No, continue'),
                    callback: function(opts, e) {
                        e.preventDefault();

                        if (opts.primary) {
                            model.set('active', false)
                            model.save();
                        }

                        if (opts.secondary) {
                            model.set('active', true)
                        }
                    }
                });
            } else {
                this.set('active', true);
            }
        },
        addProjectToMonthly: function(project){
            var store = this.get('store'),
                donation = this.get('model');
            if (donation.get('projects').anyBy('project', project)) {
               // Project already connected to this monthly donation.
            } else {
                App.MonthlyDonationProject.createRecord({project: project, donation: donation});
            }

            // Close the modal
            this.send('closeAllModals');

        }
    }

});

App.MonthlyProjectSearchFormController = App.ProjectSearchFormController.extend({
    needs: ['monthlyProjectList'],
    pageSize: 6,

    listController: function(){
        return this.get('controllers.monthlyProjectList');
    }.property()
});

App.MonthlyProjectListController = App.ProjectListController.extend({});

App.MonthlyDonationProjectController = Em.ObjectController.extend({

    actions: {
        deleteProject: function() {
            var monthlyProject = this.get('model');
            monthlyProject.deleteRecord();
            monthlyProject.save();
        }
    }
});
