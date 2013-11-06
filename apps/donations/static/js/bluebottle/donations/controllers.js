App.UserDonationController = Em.ObjectController.extend({
    needs: ['currentUser']
});

App.UserMonthlyController = Em.ObjectController.extend({

});

App.UserMonthlyProfileController = Em.ObjectController.extend(App.Editable, {
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

    addressComplete: function(){
        if (this.get('address.didError')) {
            return false;
        }
        if (this.get('address.isDirty')) {
            return false;
        }
        return (this.get('address.line1') && this.get('address.city') && this.get('address.country') && this.get('address.postal_code'));
    }.property('address.line1', 'address.city', 'address.country', 'address.postal_code'),

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
        save: function(){
            var model = this.get('model');
            var message = gettext("You're about to set a monthly donation.<br/><br/>" +
                "Has anybody ever told you that you're awesome? Well, you're awesome!<br/><br/>" +
                "1%Club will withdrawal your monthly donation from your bank account in the beginning of each month. You can cancel it anytime you like.<br/><br/>" +
                "We will send you an email in the beginning of each month to update you on what project(s) received your 1% Support!");

            var address = this.get('address');

            Bootstrap.ModalPane.popup({
                classNames: ['modal'],
                heading: gettext('Set my monthly donation'),
                message: message,
                primary: gettext('Save'),
                secondary: gettext('Cancel'),
                callback: function(opts, e) {
                    e.preventDefault();

                    if (opts.primary) {
                        model.transaction.commit();
                        address.save();
                    }

                    if (opts.secondary) {
                        // Do nothing
                    }
                }
            });

        },
        toggleActive: function(sender, value){
            if (this.get('payment.active')) {
                var payment = this.get('payment');
                Bootstrap.ModalPane.popup({
                    classNames: ['modal'],
                    heading: gettext('Stop my monthly donation'),
                    message: gettext('Thanks a lot for your support until now. You rock! We welcome you back anytime.<br /><br />Are you sure you want to stop your monthly support?'),
                    primary: gettext('Yes, stop my donation'),
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
            if (order.get('donations').anyBy('project', project)) {
               // Donation for this already exists in this order.
            } else {
                var donation = store.createRecord(App.RecurringDonation);
                order.transaction.add(donation);
                donation.set('project', project);
                donation.set('order', order);
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

App.MonthlyDonationController = Em.ObjectController.extend({
    deleteDonation: function() {
        var donation = this.get('model');
        var order = donation.get('order');
        order.transaction.add(donation);
        order.get('donations').removeObject(donation);
        donation.deleteRecord();
    }
});