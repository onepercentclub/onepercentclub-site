App.UserDonationController = Em.ObjectController.extend({
    needs: ['currentUser']
});

App.UserMonthlyController = Em.ObjectController.extend({

});

App.UserMonthlyProfileController = Em.ObjectController.extend({
    actions: {
        save: function(){
            this.get('model').save();
        }
    }
});

App.UserMonthlyProjectsController = Em.ObjectController.extend({

    initamount: function(obj, keyName) {
        if (this.get('payment.isLoaded') && this.get('amount') == 0) {
            this.set('amount', this.get('payment.amount'))
        }
    }.observes('payment.isLoaded'),

    shouldSave: function(obj, keyName){
        var dirty = false;
        this.get('model.donations').forEach(function(record){
            if (record.get('isDirty')){
                dirty = true;
            }
        });
        if (this.get('model.isDirty') || this.get('payment.isDirty')) {
            dirty = true;
        }
        return dirty;
    }.property('isDirty', 'payment.isDirty', 'model.donations.@each.isDirty'),

    updateDonations: function(obj, keyName) {

        // Validation:
        if (keyName == 'amount') {
            // Clear the previous error.
            this.set('errors', {amount: []});

            var intRegex = /^\d+$/;
            if(!intRegex.test(this.get('amount'))) {
                this.set('errors', {amount: ["Please use whole numbers for your donation."]});
            } else if (this.get('amount') < 5) {
                this.set('errors', {amount: ["Monthly donations must be above €5."]});
            }

            // TODO Validate minimum €2 per project.

            // TODO Revert old value for amount.

            // Don't continue if there's an error.
            if (this.get('errors.amount.length') != 0) {
                return;
            }
        }

        var numDonations = 0,
            amountPerProject = 0,
            donations = null,
            lastDonation = null;

        var donationsTotal = 0,
            amount = 0;
        donations = this.get('donations');

        // This happens sometimes when loading the donations list from a bookmark.
        if (Em.isNone(donations)) {
            return;
        }

        numDonations = donations.get('length');

        // Special setup when the number of donations changes.
        if (keyName == 'model.length' && numDonations > 0) {
            amount = Math.max(this.get('singleTotal'), this.get('amount'));
            this.set('payment.amount', amount);
        } else {
            donationsTotal = this.get('singleTotal');
            amount = this.get('payment.amount');
        }

        if (amount == 0) {
            amount = donationsTotal;
            this.set('payment.amount', donationsTotal);
        }

        if (donationsTotal != amount) {
            var order = this.get('model');
            amountPerProject = Math.floor(amount / numDonations);
            for (var j = 0; j < numDonations - 1; j++) {
                donations.objectAt(j).set('amount', amountPerProject);
                order.transaction.add(donations.objectAt(j));
            }
            // Update the last donation with the remaining amount if it hasn't been deleted.
            lastDonation = donations.objectAt(numDonations - 1);
            if (!Em.isNone(lastDonation)) {
                lastDonation.set('amount', amount - (amountPerProject * (numDonations - 1)));
                order.transaction.add(lastDonation);
            }
        }

    }.observes('payment.amount', 'donations.length'),

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
                    }
                    if (opts.secondary) {
                        transaction.rollback();
                    }
                }
            });
        }
     },
     actions: {
        save: function(){
            this.get('model').transaction.commit();
        },
        toggleActive: function(sender, value){
            if (this.get('payment.active')) {
                var payment = this.get('payment');
                Bootstrap.ModalPane.popup({
                    classNames: ['modal'],
                    heading: gettext('Stop monthly support?'),
                    message: gettext('Are you sure you want to stop your monthly support?'),
                    primary: gettext('Yes, stop it'),
                    secondary: gettext('No, continue'),
                    callback: function(opts, e) {
                        e.preventDefault();

                        if (opts.primary) {
                            payment.set('active', false)
                            payment.save();
                        }

                        if (opts.secondary) {
                            payment.set('active', true)
                        }
                    }
                });
            } else {
                this.set('payment.active', true);
            }
        },
        addProjectToMonthly: function(project){
            var store = this.get('store');
            var order = this.get('model');
            var donation = store.createRecord(App.RecurringDonation);
            order.transaction.add(donation);
            donation.set('project', project);
            donation.set('order', order);

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

App.MonthlyDonationController = Em.ObjectController.extend({
    deleteDonation: function() {
        var donation = this.get('model');
        donation.get('order').transaction.add(donation);
        donation.deleteRecord();
    }
});