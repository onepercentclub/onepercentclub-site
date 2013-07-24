/*
 Models
 */

App.Order = DS.Model.extend({
    url: 'fund/orders',

    status: DS.attr('string'),
    recurring: DS.attr('boolean'),
    vouchers: DS.hasMany('App.Voucher'),
    donations: DS.hasMany('App.Donation')
});


App.Donation = DS.Model.extend({
    url: 'fund/donations',

    project: DS.belongsTo('App.Project'),
    amount: DS.attr('number', {defaultValue: 20}),
    status: DS.attr('string'),
    type: DS.attr('string'),
    order: DS.belongsTo('App.Order')
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
    donations: DS.hasMany('App.CurrentOrderDonation')
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


App.DocDataDirectDebit = DS.Model.extend({
    url: 'fund/docdatadirectdebit',

    bank_account_number: DS.attr('string'),
    bank_account_name: DS.attr('string'),
    bank_account_city: DS.attr('string')
});


/*
 Controllers
 */

App.CurrentOrderDonationListController = Em.ArrayController.extend({
    // The CurrentOrderController is needed for the single / monthly radio buttons.
    needs: ['currentUser', 'currentOrder'],

    total: function() {
        return this.get('model').getEach('amount').reduce(function(accum, item) {
            // Use parseInt like this so we don't have a temporary string concatenation briefly displaying in the UI.
            return parseInt(accum) + parseInt(item);
        }, 0);
    }.property('model.@each.amount', 'model.length'),

    moreThanOneDonation: function() {
        return this.get('length') > 1;
    }.property('length'),

    monthly_total: 0,

    updateMonthlyDonations: function(obj, keyName) {
        if (!this.get('controllers.currentOrder.recurring')) {
            return;
        }

        var donationsTotal = 0;
        var monthlyTotal = 0;
        var donations = this.get('model');
        var numDonations = donations.get('length');

        // Special setup when there's a new donation added.
        if (keyName == 'model.length' && numDonations > 0 && donations.objectAt(numDonations - 1).get('isNew')) {
            monthlyTotal = this.get('monthly_total') + App.Donation.prototype.get('amount');
            this.set('monthly_total', monthlyTotal);
        } else {
            donationsTotal = this.get('total');
            monthlyTotal = this.get('monthly_total');
        }

        if (monthlyTotal == 0) {
            monthlyTotal = donationsTotal;
            this.set('monthly_total', monthlyTotal);
        }

        if (donationsTotal != monthlyTotal) {
            var amountPerProject = Math.round(monthlyTotal / numDonations);
            for (var i = 0; i < numDonations - 1; i++) {
                this.updateDonation(donations.objectAt(i), amountPerProject)
            }
            // Update the last donation with the remaining amount.
            this.updateDonation(donations.objectAt(numDonations - 1), monthlyTotal - (amountPerProject * (numDonations - 1)));
        }
    }.observes('model.length', 'monthly_total', 'controllers.currentOrder.recurring'),

    updateDonation: function(donation, newAmount) {
        if (donation.get('isNew')) {
            var controller = this;
            // Note: resolveOn is a private ember-data method.
            var donationPromise = donation.resolveOn('didCreate');
            donationPromise.then(function(donation) {
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
            record.get('stateManager').goToState('loaded');
            record.reload();

            // Clear the error after 10 seconds.
            Ember.run.later(this, function() {
                record.set('errors', []);
            }, 10000);
        });
        // Renew the transaction as needed.
        // If we have an error the record will stay 'dirty' and we can't put it into a new transaction.
        if (donation.get('transaction.isDefault')) {
            var transaction = this.get('store').transaction();
            transaction.add(donation);
        }
        donation.set('amount', newAmount);
        donation.transaction.commit();
    }
});


App.CurrentOrderDonationController = Em.ObjectController.extend({
    needs: ['currentOrder', 'currentOrderDonationList'],

    updateDonation: function(newAmount) {
        var donation = this.get('model');
        var donationListController = this.get('controllers.currentOrderDonationList');
        donationListController.updateDonation(donation, newAmount);
    },

    deleteDonation: function() {
        var transaction = this.get('store').transaction();
        var donation = this.get('model');
        transaction.add(donation);
        // Hack: Remove the donation from the current order so that ember-data doesn't get confused. This needs to be
        // done because we're not setting the proper order id (i.e. 'current') in the donation json from the server.
        var order = App.CurrentOrder.find('current');
        order.get('donations').removeObject(donation);
        donation.deleteRecord();
        transaction.commit();
    }
});


App.CurrentOrderVoucherListController = Em.ArrayController.extend({
    total: function() {
        return this.get('model').getEach('amount').reduce(function(accum, item) {
            // Use parseInt like this so we don't have a temporary string concatenation briefly displaying in the UI.
            return parseInt(accum) + parseInt(item);
        }, 0);
    }.property('model.@each.amount', 'model.length')
});


App.CurrentOrderVoucherController = Em.ObjectController.extend({
    deleteVoucher: function() {
        var transaction = this.get('store').transaction();
        var voucher = this.get('model');
        transaction.add(voucher);
        // Hack: Remove the voucher from the current order so that ember-data doesn't get confused. This needs to be
        // done because we're not setting the proper order id (i.e. 'current') in the voucher json from the server.
        var order = App.CurrentOrder.find('current');
        order.get('vouchers').removeObject(voucher);
        voucher.deleteRecord();
        transaction.commit();
    }
});


App.CurrentOrderVoucherNewController = Em.ObjectController.extend({
    needs: ['currentUser', 'currentOrder'],

    init: function() {
        this._super();
        this.createNewVoucher();
    },

    createNewVoucher: function() {
        var transaction = this.get('store').transaction();
        var voucher =  transaction.createRecord(App.CurrentOrderVoucher);
        voucher.set('sender_name', this.get('controllers.currentUser.full_name'));
        voucher.set('sender_email', this.get('controllers.currentUser.email'));
        voucher.set('receiver_name', '');
        voucher.set('receiver_email', '');
        this.set('model', voucher);
        this.set('transaction', transaction);
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

        this.get('transaction').commit();
    }
});


App.PaymentProfileController = Em.ObjectController.extend({
    needs: ['currentOrder'],

    initTransaction: function() {
        var transaction = this.get('store').transaction();
        this.set('transaction', transaction);
        transaction.add(this.get('model'));
    }.observes('model'),

    updateProfile: function() {
        var profile = this.get('model');
        // Set profile model to the 'updated' state so that the 'didUpdate' callback will always be run.
        profile.get('stateManager').goToState('updated');
        var controller = this;
        profile.one('didUpdate', function(record) {
            var currentOrder = controller.get('controllers.currentOrder');
            currentOrder.set('paymentProfileComplete', true);
            controller.transitionToRoute('paymentSelect');
        });
        profile.one('becameInvalid', function(record) {
            controller.get('model').set('errors', record.get('errors'));
            // Note: We're reusing the transaction in this case but it seems to work.
        });
        this.get('transaction').commit();
    },

    isPaymentProfileReady: function() {
        return !Em.isEmpty(this.get('firstName')) && !Em.isEmpty(this.get('lastName')) && !Em.isEmpty(this.get('email')) &&
               !Em.isEmpty(this.get('address')) && !Em.isEmpty(this.get('postalCode')) && !Em.isEmpty(this.get('city')) &&
               !Em.isEmpty(this.get('country'));
    }.property('firstName', 'lastName', 'email', 'address', 'postalCode', 'city', 'country')
});

App.PaymentSelectController = Em.ObjectController.extend({
    needs: ['currentOrder'],

// Not used for now:
//    hasIdeal: function() {
//        var availPMs = this.get('availablePaymentMethods');
//        if (availPMs) {
//            return (availPMs.contains('dd-ideal'));
//        }
//        return false;
//    }.observes('availablePaymentMethods'),
//
//    hasWebMenu: function() {
//        var availPMs = this.get('availablePaymentMethods');
//        if (availPMs) {
//            return (availPMs.contains('dd-direct-debit'));
//        }
//        return false;
//    }.observes('availablePaymentMethods'),

    displayPaymentError: function() {
        this.get('controllers.currentOrder').setProperties({
            display_message: true,
            isError: true,
            autoHideMessage: false,
            message_content: 'There was an error sending you to the payment provider. Please try again.'
        });
       this.transitionToRoute('paymentProfile')
    },

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
//                document.location = paymentUrl;
//            }
//        });
//        this.get('transaction').commit();

        // Use jQuery directly to avoid the problems with updating server-side data.
        var payment = this.get('model');
        var controller = this;
        jQuery.ajax({
            url: '/i18n/api/fund/payments/current',
            type: 'PUT',
            data: JSON.stringify({ payment_method:  payment.get('availablePaymentMethods').objectAt(0)}),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            context: this,
            success: function(json) {
                if (json['payment_url']) {
                    document.location = json['payment_url'];
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
});


App.CurrentOrderController = Em.ObjectController.extend({
    donationType: 'single',  // The default donation type.

    updateRecurring: function() {
        var order = this.get('model');
        var transaction = this.get('store').transaction();
        transaction.add(order);
        order.set('recurring', (this.get('donationType') == 'monthly'));
        transaction.commit();
    }.observes('donationType'),

    updateDonationType: function() {
        if (this.get('recurring')) {
            this.set('donationType', 'monthly')
        } else {
            this.set('donationType', 'single')
        }
    }.observes('recurring'),

    // FIXME Implement a better way to handle vouchers and donations in the order.
    // Remove donations from voucher orders and remove vouchers from donations.
    // See: https://onepercentclub.atlassian.net/browse/BB-648
    removeDonationOrVouchers: function() {
        if (this.get('isVoucherOrder') == true) {
            var donations = this.get('model.donations');
            donations.forEach(function(donation) {
                var transaction = this.get('store').transaction();
                transaction.add(donation);
                // Hack: Remove the donation from the current order so that ember-data doesn't get confused. This needs to be
                // done because we're not setting the proper order id (i.e. 'current') in the donation json from the server.
                donations.removeObject(donation);
                donation.deleteRecord();
                transaction.commit();
            }, this);
        } else if (this.get('isVoucherOrder') == false) {
            var vouchers = this.get('model.vouchers');
            vouchers.forEach(function(voucher) {
                var transaction = this.get('store').transaction();
                transaction.add(voucher);
                // Hack: Remove the voucher from the current order so that ember-data doesn't get confused. This needs to be
                // done because we're not setting the proper order id (i.e. 'current') in the voucher json from the server.
                vouchers.removeObject(voucher);
                voucher.deleteRecord();
                transaction.commit();
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


/*
 Views
 */

App.CurrentOrderView = Em.View.extend({
    templateName: 'current_order'
});


App.PaymentProfileView = Em.View.extend({
    templateName: 'payment_profile',
    tagName: 'form',

    submit: function(e) {
        e.preventDefault();
        this.get('controller').updateProfile();
    }
});


App.CurrentOrderDonationListView = Em.View.extend({
    templateName: 'current_order_donation_list',
    tagName: 'form',

    submit: function(e) {
        e.preventDefault();
    },

    change: function(e) {
        // The single / monthly change and the monthly_total change are sent here and
        // we only want to deal with the monthly_total change.
        var value = parseInt(Em.get(e, 'target.value'));
        if (Em.typeOf(value) === 'number' && !isNaN(value)) {
            this.get('controller').set('monthly_total', value);
        }
    }
});


App.CurrentOrderVoucherListView = Em.View.extend({
    templateName: 'current_order_voucher_list',
    classNames: ['content']
});


App.OrderThanksView = Em.View.extend({
    templateName: 'order_thanks'
});


App.CurrentOrderDonationView = Em.View.extend({
    templateName: 'current_order_donation',
    tagName: 'li',
    classNames: 'donation-project control-group',

    change: function(e) {
        this.get('controller').updateDonation(Em.get(e, 'target.value'));
    },

    delete: function(item) {
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

    delete: function() {
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


App.PaymentSelectView = Em.View.extend({
    templateName: 'paymentSelect',
    classNames: ['content']
});


App.IdealPaymentMethodInfoView = Em.View.extend({
    templateName: 'ideal_payment_method_info',
    tagName: 'form',

    submit: function(e) {
        e.preventDefault();
    }
});


App.DirectDebitPaymentMethodInfoView = Em.View.extend({
    templateName: 'direct_debit_payment_method_info',
    tagName: 'form',

    submit: function(e){
        e.preventDefault();
    }
});

