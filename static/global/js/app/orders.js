/*
 Models
 */

App.Order = DS.Model.extend({
    url: 'fund/orders',

    status: DS.attr('string'),
    recurring: DS.attr('boolean'),
    vouchers: DS.hasMany('App.Voucher'),
    donations: DS.hasMany('App.Donation'),
    created: DS.attr('date'),
    total: DS.attr('number')
});


App.Donation = DS.Model.extend({
    url: 'fund/donations',

    project: DS.belongsTo('App.Project'),
    amount: DS.attr('number', {defaultValue: 20}),
    status: DS.attr('string'),
    type: DS.attr('string'),
    order: DS.belongsTo('App.Order')
});


App.Ticker = DS.Model.extend({
    url: 'fund/latest-donations',
    project: DS.belongsTo('App.ProjectPreview'),
    user: DS.belongsTo('App.UserPreview'),
    amount: DS.attr('number'),
    created: DS.attr('date')
});



App.Voucher =  DS.Model.extend({
    url: 'fund/vouchers',

    receiver_name: DS.attr('string', {defaultValue: ''}),
    receiver_email: DS.attr('string'),
    sender_name: DS.attr('string', {defaultValue: ''}),
    sender_email: DS.attr('string'),
    message: DS.attr('string', {defaultValue: ''}),
    language: DS.attr('string', {defaultValue: 'en'}),
    amount: DS.attr('number', {defaultValue: 25}),
    status: DS.attr('string'),

    order: DS.belongsTo('App.Order'),
    donations: DS.hasMany('App.VoucherDonation')

});


/* Models with CurrentOrder relations and urls. */

// FIXME Get rid of CurrentOrder models

App.CurrentOrder = App.Order.extend({
    url: 'fund/orders',

    vouchers: DS.hasMany('App.CurrentOrderVoucher'),
    donations: DS.hasMany('App.CurrentOrderDonation'),

    // This is a hack to work around an issue with Ember-Data keeping the id as 'current'.
    // App.UserSettingsModel.find(App.CurrentUser.find('current').get('id_for_ember'));
    id_for_ember: DS.attr('number')
});


App.CurrentOrderDonation = App.Donation.extend({
    url: 'fund/orders/current/donations',

    order: DS.belongsTo('App.CurrentOrder')
});


App.CurrentOrderVoucher = App.Voucher.extend({
    url: 'fund/orders/current/vouchers',

    order: DS.belongsTo('App.CurrentOrder')
});


/* Models related to payments. */

App.PaymentProfile = DS.Model.extend({
    url: 'fund/paymentprofiles',

    firstName: DS.attr('string'),
    lastName: DS.attr('string'),
    email: DS.attr('string'),
    address: DS.attr('string'),
    postalCode: DS.attr('string'),
    city: DS.attr('string'),
    country: DS.attr('string')
});


App.Payment = DS.Model.extend({
    url: 'fund/payments',

    paymentMethod: DS.attr('string'),
    paymentSubmethod: DS.attr('string'),
    paymentUrl: DS.attr('string'),
    availablePaymentMethods: DS.attr('array')
});


App.RecurringDirectDebitPayment = DS.Model.extend({
    url: 'fund/recurringdirectdebitpayments',

    active: DS.attr('boolean'),
    amount: DS.attr('number'),

    name: DS.attr('string'),
    city: DS.attr('string'),
    account: DS.attr('string')
});


/*
 Controllers
 */

App.CurrentOrderDonationListController = Em.ArrayController.extend({
    // The CurrentOrderController is needed for the single / recurring radio buttons.
    needs: ['currentUser', 'currentOrder'],

    singleTotal: function() {
        return this.get('model').getEach('amount').reduce(function(accum, item) {
            // Use parseInt like this so we don't have a temporary string concatenation briefly displaying in the UI.
            return parseInt(accum) + parseInt(item);
        }, 0);
    }.property('model.@each.amount', 'model.length'),

    moreThanOneDonation: function() {
        return this.get('length') > 1;
    }.property('length'),

    showTopThreeProjects: function() {
        var recurringOrderEmpty = true;
        if (!Em.isNone(this.get('recurringOrder'))) {
            // Monthly donation order already set.
            var tempTotal = 0;
            this.get('recurringOrder.donations').forEach(function(donation) {
                tempTotal += donation.get('tempRecurringAmount');
            });
            recurringOrderEmpty = this.get('recurringOrder.donations.length') == 0 || tempTotal == 0;
        }
        return this.get('controllers.currentOrder.recurring') && this.get('length') == 0 && recurringOrderEmpty;
    }.property('controllers.currentOrder.recurring', 'length', 'recurringOrder.donations.length', 'recurringOrder.donations.@each.tempRecurringAmount'),

    editingRecurringOrder: function(obj, keyName) {
        // True when modifying an existing order that has donations. False otherwise (including when modifying a top three projects recurringPayment).
        return this.get('controllers.currentOrder.recurring') && this.get('recurringOrder.donations.length') > 0;
    }.property('controllers.currentOrder.recurring', 'recurringOrder.donations.length', 'recurringPayment', 'isLoaded'),

    readyForPayment: function() {
        if (this.get('length') > 0) {
            return true;
        }
        if (this.get('editingRecurringOrder')) {
            if (this.get('recurringTotal') != this.get('recurringOrder.total')) {
                return true;
            }
        }
        return this.get('recurringTotal') > 0;
    }.property('length', 'editingRecurringOrder', 'recurringTotal'),

    recurringTotal: 0,

    initRecurringTotal: function(obj, keyName) {
        if (this.get('recurringPayment.isLoaded') && this.get('recurringTotal') == 0) {
            this.set('recurringTotal', this.get('recurringPayment.amount'))
        }
    }.observes('recurringPayment.isLoaded'),

    updateRecurringDonations: function(obj, keyName) {
        if (!this.get('controllers.currentOrder.recurring')) {
            return;
        }

        // Validation:
        if (keyName == 'recurringTotal') {
            // Clear the previous error.
            this.set('errors', {recurringTotal: []});

            var intRegex = /^\d+$/;
            if(!intRegex.test(this.get('recurringTotal'))) {
                this.set('errors', {recurringTotal: ["Please use whole numbers for your donation."]});
            } else if (this.get('recurringTotal') < 5) {
                this.set('errors', {recurringTotal: ["Monthly donations must be above €5."]});
            }

            // TODO Validate minimum €2 per project.

            // TODO Revert old value for recurringTotal.

            // Don't continue if there's an error.
            if (this.get('errors.recurringTotal.length') != 0) {
                return;
            }
        }

        var numDonations = 0,
            amountPerProject = 0,
            donations = null,
            lastDonation = null;

        if (this.get('editingRecurringOrder')) {
            // The user already has a recurring order set.
            if (this.get('recurringTotal') == 0) {
                this.set('recurringTotal', this.get('recurringOrder.total'));
            }

            // Create a donations list with the new and monthly donations.
            donations = Em.A();
            donations.addObjects(this.get('model'));
            this.get('recurringOrder.donations').forEach(function(donation) {
                // Don't include donations set to 0 as they have been 'deleted'.
                if (donation.get('tempRecurringAmount') != 0) {
                    donations.addObject(donation);
                }
            });
            numDonations =  donations.get('length');

            // Set the updated monthly totals in a
            amountPerProject = Math.floor(this.get('recurringTotal') / numDonations);
            for (var i = 0; i <  donations.get('length') - 1; i++) {
                donations.objectAt(i).set('tempRecurringAmount', amountPerProject);
            }
            // Update the last donation with the remaining amount if it hasn't been deleted.
            lastDonation = donations.objectAt(donations.get('length') - 1);
            if (!Em.isNone(lastDonation)) {
                lastDonation.set('tempRecurringAmount', this.get('recurringTotal') - (amountPerProject * (numDonations - 1)));
            }
        } else {
            // The user does not already have a recurring order set or the user is support the top three projects.
            var donationsTotal = 0,
                recurringTotal = 0;
            donations = this.get('model');

            // This happens sometimes when loading the donations list from a bookmark.
            if (Em.isNone(donations)) {
                return;
            }

            numDonations = donations.get('length');

            // Special setup when the number of donations changes.
            if (keyName == 'model.length' && numDonations > 0) {
                recurringTotal = Math.max(this.get('singleTotal'), this.get('recurringTotal'));
                this.set('recurringTotal', recurringTotal);
            } else {
                donationsTotal = this.get('singleTotal');
                recurringTotal = this.get('recurringTotal');
            }

            if (recurringTotal == 0) {
                recurringTotal = donationsTotal;
                this.set('recurringTotal', donationsTotal);
            }

            if (donationsTotal != recurringTotal) {
                amountPerProject = Math.floor(recurringTotal / numDonations);
                for (var j = 0; j < numDonations - 1; j++) {
                    this.updateDonation(donations.objectAt(j), amountPerProject)
                }
                // Update the last donation with the remaining amount if it hasn't been deleted.
                lastDonation = donations.objectAt(numDonations - 1);
                if (!Em.isNone(lastDonation)) {
                    this.updateDonation(lastDonation, recurringTotal - (amountPerProject * (numDonations - 1)));
                }
            }
        }

    }.observes('length', 'recurringTotal', 'controllers.currentOrder.recurring', 'recurringOrder.donations.length'),

    updateDonation: function(donation, newAmount) {
        // 'current' order id hack: This can be removed when we have a RESTful Order API.
        if (Em.isNone(donation)) {
            return;
        }

        if (donation.get('isNew')) {
            var controller = this;
            // Note: resolveOn is a private ember-data method.
            donation.resolveOn('didCreate').then(function(donation) {
                controller.updateCreatedDonation(donation, newAmount)
            });
         } else {
            this.updateCreatedDonation(donation, newAmount)
        }
    },

    updateCreatedDonation: function(donation, newAmount) {
        // Does not work if donation 'isNew' is true.
        donation.set('errors', []);
        donation.one('becameInvalid', function(record) {
            record.set('errors', record.get('errors'));

            // Revert to the value on the server when there's an error.
            record.transitionTo('loaded');
            record.reload();

            // Clear the error after 10 seconds.
            Ember.run.later(this, function() {
                record.set('errors', []);
            }, 10000);
        });
        donation.set('amount', newAmount);
        donation.save();
    }
});


App.CurrentOrderDonationController = Em.ObjectController.extend({
    needs: ['currentOrder', 'currentOrderDonationList'],

    updateDonation: function(newAmount) {
        var donation = this.get('model');

        var intRegex = /^\d+$/;
        if(intRegex.test(newAmount)) {
            var donationListController = this.get('controllers.currentOrderDonationList');
            donationListController.updateDonation(donation, newAmount);
        } else {
            donation.set('errors', {amount: ["Please use whole numbers for your donation."]});

            // Revert to the value on the server when there's an error.
            donation.transitionTo('loaded');
            donation.reload();

            // Clear the error after 10 seconds.
            Ember.run.later(this, function() {
                donation.set('errors', []);
            }, 10000);
        }
    },

    deleteDonation: function() {
        var donation = this.get('model');
        donation.deleteRecord();
        donation.save();
    }
});

App.CurrentRecurringDonationController = App.CurrentOrderDonationController.extend({
    deleteDonation: function() {
        var donation = this.get('model');
        donation.set('tempRecurringAmount', 0);
        this.get('controllers.currentOrderDonationList').updateRecurringDonations()
    }
});


App.CurrentOrderVoucherListController = Em.ArrayController.extend({
    singleTotal: function() {
        return this.get('model').getEach('amount').reduce(function(accum, item) {
            // Use parseInt like this so we don't have a temporary string concatenation briefly displaying in the UI.
            return parseInt(accum) + parseInt(item);
        }, 0);
    }.property('model.@each.amount', 'model.length')
});


App.CurrentOrderVoucherController = Em.ObjectController.extend({
    deleteVoucher: function() {
        var voucher = this.get('model');
        voucher.deleteRecord();
        voucher.save();
    }
});


App.CurrentOrderVoucherNewController = Em.ObjectController.extend({
    needs: ['currentUser', 'currentOrder'],

    init: function() {
        this._super();
        this.createNewVoucher();
    },

    createNewVoucher: function() {
        var store = this.get('store');
        var voucher =  store.createRecord(App.CurrentOrderVoucher);
        voucher.set('sender_name', this.get('controllers.currentUser.full_name'));
        voucher.set('sender_email', this.get('controllers.currentUser.email'));
        voucher.set('receiver_name', '');
        voucher.set('receiver_email', '');
        this.set('model', voucher);
    },

    updateSender: function(){
        // Make sure the sender info is fully loaded on refresh
        var voucher = this.get('model');
        voucher.set('sender_name', this.get('controllers.currentUser.full_name'));
        voucher.set('sender_email', this.get('controllers.currentUser.email'));
    }.observes('controllers.currentUser.email', 'controllers.currentUser.full_name'),

    addVoucher: function() {
        var voucher = this.get('model');
        // Set the order so the list gets updated in the view
        var order = this.get('controllers.currentOrder.model');
        voucher.set('order', order);

        var controller = this;
        voucher.on('didCreate', function(record) {
            controller.createNewVoucher();
            controller.set('sender_name', record.get('sender_name'));
            controller.set('sender_email', record.get('sender_email'));
        });
        voucher.on('becameInvalid', function(record) {
            controller.createNewVoucher();
            controller.get('model').set('errors', record.get('errors'));
            record.deleteRecord();
        });

        voucher.save();
    }
});


App.PaymentProfileController = Em.ObjectController.extend({
    needs: ['currentOrder', 'currentUser'],

    updateProfile: function() {
        var profile = this.get('model');
        var user = this.get('controllers.currentUser');

        // Set profile model to the 'updated' state so that the 'didUpdate' callback will always be run.
        profile.transitionTo('updated.uncommitted');

        var controller = this;
        profile.one('didUpdate', function(record) {
            var currentOrder = controller.get('controllers.currentOrder');
            currentOrder.set('paymentProfileComplete', true);
            if (user.get('isAuthenticated')) {
                controller.transitionToRoute('paymentSelect');
            } else {
                controller.transitionToRoute('paymentSignup');
            }
        });

        profile.one('becameInvalid', function(record) {
            controller.get('model').set('errors', record.get('errors'));
        });

        profile.save();
    },

    isFormReady: function() {
        return !Em.isEmpty(this.get('firstName')) && !Em.isEmpty(this.get('lastName')) && !Em.isEmpty(this.get('email')) &&
               !Em.isEmpty(this.get('address')) && !Em.isEmpty(this.get('postalCode')) && !Em.isEmpty(this.get('city')) &&
               !Em.isEmpty(this.get('country'));
    }.property('firstName', 'lastName', 'email', 'address', 'postalCode', 'city', 'country')
});


App.PaymentSignupController = Em.ObjectController.extend({
    needs: ['paymentProfile', 'currentUser'],

    createUser: function() {
        var user = this.get('model');
        var controller = this;
        user.one('didCreate', function(user) {
            controller.transitionToRoute('paymentSelect');
        });
        user.one('becameInvalid', function(record) {
            controller.get('model').set('errors', record.get('errors'));
        });
        user.save();
    },

    isFormReady: function() {
        return !Em.isEmpty(this.get('email')) && !Em.isEmpty(this.get('password')) && !Em.isEmpty(this.get('password2'));
    }.property('email', 'password', 'password2')
});


App.PaymentSelectController = Em.ObjectController.extend({
    needs: ['currentOrder'],

    displayPaymentError: function() {
        this.get('controllers.currentOrder').setProperties({
            display_message: true,
            isError: true,
            autoHideMessage: false,
            message_content: 'There was an error sending you to the payment provider. Please try again.'
        });
       this.transitionToRoute('paymentProfile')
    },

    actions: {

        proceedWithPayment: function() {
            this.set('paymentInProgress', true);
    // FIXME Figure out the problem with Ember Data and re-enable this code.
    //        var transaction = this.get('store').transaction();
    //        var payment = this.get('model');
    //        transaction.add(payment);
    //        payment.set('paymentMethod', payment.get('availablePaymentMethods').objectAt(0));
    //        var controller = this;
    //        payment.one('didUpdate', function(record) {
    //            var paymentUrl = record.get('paymentUrl');
    //            if (paymentUrl) {
    //                    window.location = json['payment_url'];
    //            }
    //        });
    //        this.get('transaction').commit();

            // Use jQuery directly to avoid the problems with updating server-side data.
            var payment = this.get('model');
            var controller = this;
            jQuery.ajax({
                url: '/api/fund/payments/current',
                type: 'PUT',
                data: JSON.stringify({ payment_method:  payment.get('availablePaymentMethods').objectAt(0)}),
                dataType: 'json',
                contentType: 'application/json; charset=utf-8',
                context: this,
                success: function(json) {
                    if (json['payment_url']) {
                        window.location = json['payment_url'];
                    } else {
                        controller.set('paymentInProgress', false);
                        controller.displayPaymentError();
                    }
                },
                error: function(xhr) {
                    controller.set('paymentInProgress', false);
                    controller.displayPaymentError();
                }
            });
        }
    }
});


App.RecurringDirectDebitPaymentController = Em.ObjectController.extend({
    needs: ['currentOrder', 'currentOrderDonationList'],

    setRecurringOrder: function() {
        this.set('paymentInProgress', true);
        function transitionToThanks(controller){
            // FIXME: Ember has a hard time dealing with the current order changing. A sever-side post_save action to
            // the RecurringDirectDebitPayment moves the donations from 'current' Order to the recurring order. A reload
            // of the 'current' Order and a transition doesn't seem to work. This could be fixed if we move to a RESTful
            // Order process.
            //   controller.get('controllers.currentOrder.model').reload();
            //   controller.transitionToRoute('recurringOrderThanks');
            var thanksUrl = window.location.origin + window.location.pathname + window.location.hash.split('/')[0] + '/support/monthly/thanks';

            if (controller.get('controllers.currentOrderDonationList.editingRecurringOrder')) {
                var donations = Em.A();
                donations.addObjects(controller.get('controllers.currentOrderDonationList.model'));
                donations.addObjects(controller.get('controllers.currentOrderDonationList.recurringOrder.donations'));

                donations.forEach(function(donation) {
                    if (donation.get('amount') != donation.get('tempRecurringAmount')) {
                        // The donation won't be in current order anymore so we need to use the generic donations api.
                        if (donation.get('url').indexOf('current') !== -1) {
                            donation.set('url', donation.get('url').replace('orders/current/', ''));
                        }

                        // Update or delete the donations.
                        if (donation.get('tempRecurringAmount') == 0) {
                            // Delete donations set to 0.
                            donation.deleteRecord();
                            donation.save();
                        } else {
                            // Update donation when amount is greater than 0.
                            controller.get('controllers.currentOrderDonationList').updateDonation(donation, donation.get('tempRecurringAmount'))
                        }
                    }
                });
                // FIXME: Need to only load thanks page when all donations update successfully. No time to implement this.
                // FIXME: Set payment error error message when there's an error updating the donation.
                Em.run.later(function(){
                    window.location = thanksUrl;
                    window.location.reload(true);
                }, 5000);
            } else {
                window.location = thanksUrl;
                window.location.reload(true);
            }
        }

        var controller = this;
        var recurringDirectDebitPayment = this.get('model');
        recurringDirectDebitPayment.set('active', true);
        recurringDirectDebitPayment.set('amount', controller.get('controllers.currentOrderDonationList.recurringTotal'));

        recurringDirectDebitPayment.one('becameInvalid', function(record) {
            // FIXME: turn off didCreate, didUpdate
            controller.set('paymentInProgress', false);
            controller.get('model').set('errors', record.get('errors'));
            record.transitionTo('created');
        });
        recurringDirectDebitPayment.one('didCreate', function(record) {
            // FIXME: turn off becameInvalid, didUpdate
            transitionToThanks(controller)
        });
        recurringDirectDebitPayment.one('didUpdate', function(record) {
            // FIXME: turn off didCreate, becameInvalid
            transitionToThanks(controller)
        });

        if(!recurringDirectDebitPayment.get('isNew')) {
            // Set recurringDirectDebitPayment model to the 'updated' state so that the 'didUpdate' callback will always be run.
            recurringDirectDebitPayment.transitionTo('updated');
        }

        recurringDirectDebitPayment.save();
    },

    isFormReady: function() {
        return !Em.isEmpty(this.get('name')) && !Em.isEmpty(this.get('city')) && !Em.isEmpty(this.get('account'));
    }.property('name', 'city', 'account')
});


App.CurrentOrderController = Em.ObjectController.extend({
    needs: ['currentUser'],
    donationType: '',

    updateRecurring: function() {
        var order = this.get('model');
        if (!Em.isNone(order)) {
            order.set('recurring', (this.get('donationType') == 'monthly'));
            order.save();
        }
    }.observes('donationType'),

    // Ensures the single / monthly toggle is initialized correctly when loading donations from bookmark.
    initDonationType: function() {
        if (this.get('donationType') == '') {
            if (this.get('recurring')) {
                this.set('donationType', 'monthly')
            } else {
                this.set('donationType', 'single')
            }
        }
    }.observes('model'),

    // FIXME Implement a better way to handle vouchers and donations in the order.
    // Remove donations from voucher orders and remove vouchers from donations.
    // See: https://onepercentclub.atlassian.net/browse/BB-648
    removeDonationOrVouchers: function() {
        if (this.get('isVoucherOrder') == true) {
            var donations = this.get('donations');
            donations.forEach(function(donation) {
                donation.deleteRecord();
                donation.save();
            }, this);
        } else if (this.get('isVoucherOrder') == false) {
            var vouchers = this.get('vouchers');
            vouchers.forEach(function(voucher) {
                voucher.deleteRecord();
                voucher.save();
            }, this);
        }
    }.observes('isVoucherOrder'),

    // Display messages inline similar to the message display in the ApplicationController.
    display_message: false,
    isError: false,
    autoHideMessage: false,

    displayMessage: (function() {
        if (this.get('display_message') == true) {
            if (this.get('autoHideMessage')) {
                Ember.run.later(this, function() {
                    this.hideMessage();
                }, 10000);
            }
        }
    }).observes('display_message'),

    hideMessage: function() {
        this.set('display_message', false);
    }
});


App.OrderThanksController = Em.ObjectController.extend({
    needs: ['currentUser']
});


App.RecurringOrderThanksController = Em.ObjectController.extend({
    needs: ['currentUser'],

    moreThanOneDonation: function() {
        return this.get('donations.length') > 1;
    }.property('length')
});


App.TickerController = Em.ArrayController.extend(Ember.SortableMixin, {

    sortProperties: ['created'],
    sortAscending: false,
    init: function(){
        this._super();
        var controller = this;
        window.setTimeout(function(){
            controller.refresh();
            console.log('reloading');
        }, 5000);
    },

    refresh: function(){
        var controller = this;
        App.Ticker.find();
        window.setTimeout(function(){
            controller.refresh();
            console.log('reloading');
        }, 20000);

    }


});

/*
 Views
 */

App.PaymentProfileView = Em.View.extend({
    submit: function(e) {
        e.preventDefault();
        this.get('controller').updateProfile();
    }
});

App.PaymentSignupView = Em.View.extend({
    submit: function(e) {
        e.preventDefault();
        this.get('controller').createUser();
    }
});


App.CurrentOrderDonationListView = Em.View.extend({
    templateName: 'current_order_donation_list',

    submit: function(e) {
        e.preventDefault();
    },

    change: function(e) {
        // The "single" / "monthly" change (strings) and the recurringTotal change (number) are sent here and
        // we only want to deal with the recurringTotal change.
        var value = parseInt(Em.get(e, 'target.value'));
        if (Em.typeOf(value) === 'number' && !isNaN(value)) {
            this.get('controller').set('recurringTotal', value);
        }
    }
});


App.CurrentOrderVoucherListView = Em.View.extend({
    templateName: 'current_order_voucher_list',
    classNames: ['content']
});


App.CurrentOrderDonationView = Em.View.extend({
    tagName: 'li',
    classNames: 'donation-project control-group',

    change: function(e) {
        this.get('controller').updateDonation(Em.get(e, 'target.value'));
    },

    'delete': function(item) {
        var controller = this.get('controller');
        this.$().slideUp(500, function() {
            controller.deleteDonation();
        });
    }
});


App.CurrentRecurringDonationView = App.CurrentOrderDonationView.extend({
    templateName: 'currentOrderDonation',

    'delete': function(item) {
        var controller = this.get('controller');
        this.$().slideUp(500, function() {
            controller.deleteDonation();
        });
    }
});


App.CurrentOrderVoucherView = Em.View.extend({
    templateName: 'current_order_voucher',
    tagName: 'li',
    classNames: ['voucher-item'],

    'delete': function() {
        var controller = this.get('controller');
        this.$().slideUp(500, function() {
            controller.deleteVoucher()
        });
    }
});


App.CurrentOrderVoucherNewView = Em.View.extend({
    templateName: 'current_order_voucher_new',
    tagName: 'form',
    classNames: ['labeled'],

    submit: function(e) {
        e.preventDefault();
    }
});


App.OrderNavView = Ember.View.extend({
    tagName: 'li',

    didInsertElement: function () {
        this._super();
        if (this.get('childViews.firstObject.active')) {
            this.setOrderProgress();
        }
    },

    childBecameActive: function(sender, key) {
        if (this.get(key) && this.state == "inDOM") {
            this.setOrderProgress()
        }
    }.observes('childViews.firstObject.active'),

    setOrderProgress: function() {
        var highlightClassName = 'is-selected';
        this.$().prevAll().addClass(highlightClassName);
        this.$().nextAll().removeClass(highlightClassName);
        this.$().addClass(highlightClassName);
    }
});


App.RecurringDirectDebitPaymentView = Em.View.extend({
    submit: function(e) {
        e.preventDefault();
        this.get('controller').setRecurringOrder();
    }
});


App.TickerView = Em.View.extend({
    // Remove header/footer for this view.
    didInsertElement: function () {
        this._super();
        $('body').css('overflow', 'hidden');
        $('#navigation').remove();
        $('#footer').remove();
    }
});

