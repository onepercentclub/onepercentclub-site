App.UserDonationController = Em.ObjectController.extend({
    needs: ['currentUser']
});

App.UserMonthlyController = Em.ObjectController.extend({
<<<<<<< HEAD

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
=======
    isActive: function(){
        if (this.get('active')) {
            return 'on';
        }
        return 'off';
    }.property('active'),

    initamount: function(obj, keyName) {
        if (this.get('recurringPayment.isLoaded') && this.get('amount') == 0) {
            this.set('amount', this.get('recurringPayment.amount'))
        }
    }.observes('recurringPayment.isLoaded'),

    updateRecurringDonations: function(obj, keyName) {
>>>>>>> 44a267a... Create separate page for monthly donation

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

<<<<<<< HEAD
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

=======
        if (this.get('editingRecurringOrder')) {
            // The user already has a recurring order set.

            // Create a donations list with the new and monthly donations.
            donations = Em.A();
            donations.addObjects(this.get('order.donations'));
            this.get('order.donations').forEach(function(donation) {
                // Don't include donations set to 0 as they have been 'deleted'.
                if (donation.get('tempRecurringAmount') != 0) {
                    donations.addObject(donation);
                }
            });
            numDonations =  donations.get('length');

            // Set the updated monthly totals in a
            amountPerProject = Math.floor(this.get('amount') / numDonations);
            for (var i = 0; i <  donations.get('length') - 1; i++) {
                donations.objectAt(i).set('tempRecurringAmount', amountPerProject);
            }
            // Update the last donation with the remaining amount if it hasn't been deleted.
            lastDonation = donations.objectAt(donations.get('length') - 1);
            if (!Em.isNone(lastDonation)) {
                lastDonation.set('tempRecurringAmount', this.get('amount') - (amountPerProject * (numDonations - 1)));
            }
        } else {
            // The user does not already have a recurring order set or the user is support the top three projects.
            var donationsTotal = 0,
                amount = 0;
            donations = this.get('order.donations');

            // This happens sometimes when loading the donations list from a bookmark.
            if (Em.isNone(donations)) {
                return;
            }

            numDonations = donations.get('length');

            // Special setup when the number of donations changes.
            if (keyName == 'model.length' && numDonations > 0) {
                amount = Math.max(this.get('singleTotal'), this.get('amount'));
                this.set('amount', amount);
            } else {
                donationsTotal = this.get('singleTotal');
                amount = this.get('amount');
            }

            if (amount == 0) {
                amount = donationsTotal;
                this.set('amount', donationsTotal);
            }

            if (donationsTotal != amount) {
                amountPerProject = Math.floor(amount / numDonations);
                for (var j = 0; j < numDonations - 1; j++) {
                    donations.objectAt(j).set('amount', amountPerProject);
                }
                // Update the last donation with the remaining amount if it hasn't been deleted.
                lastDonation = donations.objectAt(numDonations - 1);
                if (!Em.isNone(lastDonation)) {
                    lastDonation.set('amount', amount - (amountPerProject * (numDonations - 1)));
                }
            }
        }

    }.observes('amount', 'order.donations.length'),

    toggleActive: function(sender, value){
        if (value == 'on') this.set('active', true);
        if (value == 'off') this.set('active', false);
    }.observes('activeValue'),

    actions: {
        save: function(){
            this.get('model').save();
        },
        addProjectToMonthly: function(project){
            var store = this.get('store');
            var order = this.get('order');
            var donation = store.createRecord(App.MonthlyOrderDonation);
            donation.set('project', project);
            donation.set('order', order);
            donation.save();
>>>>>>> 44a267a... Create separate page for monthly donation
        }
    }

});

<<<<<<< HEAD
=======
App.UserMonthlyProfileController = App.UserMonthlyController.extend({});

App.UserMonthlyProjectsController = App.UserMonthlyController.extend({});

>>>>>>> 44a267a... Create separate page for monthly donation

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
<<<<<<< HEAD
        donation.get('order').transaction.add(donation);
        donation.deleteRecord();
=======
        // Fix because reverse relations aren't cleared.
        // See: http://stackoverflow.com/questions/18806533/deleterecord-does-not-remove-record-from-hasmany
        donation.get('order.donations').removeObject(donation);
        donation.deleteRecord();
        donation.save();
>>>>>>> 44a267a... Create separate page for monthly donation
    }
});