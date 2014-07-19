/*
 Controllers
 */

App.CurrentOrderDonationListController = Em.ArrayController.extend({
    // The CurrentOrderController is needed for the single / recurring radio buttons.
    needs: ['currentOrder', 'paymentProfile'],

    singleTotal: function() {
        return this.get('model').getEach('amount').reduce(function(accum, item) {
            // Use parseInt like this so we don't have a temporary string concatenation briefly displaying in the UI.
            return parseInt(accum) + parseInt(item);
        }, 0);
    }.property('model.@each.amount', 'model.length'),

    moreThanOneDonation: function() {
        return this.get('length') > 1;
    }.property('length'),

    readyForPayment: function() {
        var ready = true;
        if (this.get('length') === 0 ) {
            ready = false;
        }

        this.get('model').forEach(function(don){
            if (don.get('errors.amount')) {
                ready = false;
            }
        });
        return ready;
    }.property('length', 'model.@each.errors'),

    updateDonation: function(donation, newAmount) {
        // 'current' order id hack: This can be removed when we have a RESTful Order API.
        if (Em.isNone(donation)) {
            return;
        }

        if (donation.get('isNew')) {
            var controller = this;
            // Note: resolveOn is a private ember-data method.
            donation.resolveOn('didCreate').then(function(donation) {
                controller.updateCreatedDonation(donation, newAmount);
            });
         } else {
            this.updateCreatedDonation(donation, newAmount);
        }
    },
    updateCreatedDonation: function(donation, newAmount) {
        // Does not work if donation 'isNew' is true.
        donation.set('errors', []);
        donation.one('becameInvalid', function(record) {
            record.set('errors', record.get('errors'));

            // Clear the error after 10 seconds.
            Ember.run.later(this, function() {
                record.set('errors', []);
            }, 10000);
        });
        donation.set('amount', newAmount);
        donation.save();
    },
    actions: {
        nextStep: function(){
            // Check what information is available and continue to the next applicable step.
            var controller = this;
            if (this.get('paymentProfile.isComplete')){
                controller.transitionToRoute('paymentSelect');
            } else {
                controller.transitionToRoute('paymentProfile');
            }
        }
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
        // Fix because reverse relations aren't cleared.
        // See: http://stackoverflow.com/questions/18806533/deleterecord-does-not-remove-record-from-hasmany
        donation.get('order.donations').removeObject(donation);
        donation.deleteRecord();
        donation.save();
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
    needs: ['currentOrder'],

    init: function() {
        this._super();
        this.createNewVoucher();
    },

    createNewVoucher: function() {
        var store = this.get('store');
        var voucher =  store.createRecord(App.CurrentOrderVoucher);
        voucher.set('sender_name', this.get('currentUser.full_name'));
        voucher.set('sender_email', this.get('currentUser.email'));
        voucher.set('receiver_name', '');
        voucher.set('receiver_email', '');
        this.set('model', voucher);
    },

    updateSender: function(){
        // Make sure the sender info is fully loaded on refresh
        var voucher = this.get('model');
        voucher.set('sender_name', this.get('currentUser.full_name'));
        voucher.set('sender_email', this.get('currentUser.email'));
    }.observes('currentUser.email', 'currentUser.full_name'),

    addVoucher: function() {
        var voucher = this.get('model');
        // Set the order so the list gets updated in the view
        var order = this.get('currentOrder.model');
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
    needs: ['currentOrder'],

    updateProfile: function() {
        var _this = this,
            profile = this.get('model');

        // Return early if the record is still saving
        // FIXME: this is a work-around until we correctly handle saving orders by 
        //        disabling buttons / showing loading animations etc.
        if (profile.get('isSaving')) return;

        if (profile.get('isDirty')){
            // Set profile model to the uncommitted state - this is required as the
            // old version of ember data we use doesn't handle transitioning to willCommit
            // from an invalid state. This happens with server side validations.
            // See: https://github.com/emberjs/data/pull/1889
            profile.transitionTo('updated.uncommitted');
            profile.set('errors', null);
        } else {
            // Early redirect if the record is saved / unchanged
            this._successTransition();
        }

        // Save and transition on success.
        profile.save().then(function(record) {
            _this._successTransition();
        });
    },

    _successTransition: function () {
        var user = this.get('currentUser.model');

        if (user && user.get('isAuthenticated')) {
            this.transitionToRoute('paymentSelect');
        } else {
            this.transitionToRoute('paymentSignup');
        }
    },

    actions: {
        nextStep: function(){
            var profile = this.get('model');
            var user = this.get('currentUser.model');
            var controller = this;

            if (profile.get('isDirty')) {
                profile.one('didUpdate', function(record) {
                    var currentOrder = controller.get('controllers.currentOrder');
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
            }
            if (profile.get('isComplete')){
                if (user.get('isAuthenticated')) {
                    controller.transitionToRoute('paymentSelect');
                } else {
                    controller.transitionToRoute('paymentSignup');
                }
            }
        }
    }
});


App.PaymentSignupController = Em.ObjectController.extend({
    needs: ['paymentProfile'],

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
    needs: ['paymentProfile', 'currentOrder'],

    redirectPaymentMethods: function(){
        if (this.get('paymentProfile.country') == 'NL') {
            return [
                {'id':'IDEAL', 'name': 'IDEAL'},
                {'id':'SEPA_DIRECT_DEBIT', 'name': 'Automatische Incasso'},
                {'id':'MASTERCARD', 'name': 'Mastercard'},
                {'id':'VISA', 'name': 'Visa'}
            ];
        } else {
            return [
                {'id':'MASTERCARD', 'name': 'Mastercard'},
                {'id':'VISA', 'name': 'Visa'}
            ];

        }
    }.property('controllers.paymentProfile.country'),

    idealIssuers: function(){
        if (DEBUG) {
            return  [
                {'id':'ASNBNL21', 'name': 'ASN Bank'},
                {'id':'INGBNL2A', 'name': 'ING Bank'},
                {'id':'RABONL2U', 'name': 'Rabobank'},
                {'id':'RBRBNL21', 'name': 'Regio Bank'},
                {'id':'TRIONL2U', 'name': 'Triodos Bank'},
            ];
        } else {
            return  [
                {'id':'ABNANL2A', 'name': 'ABN Amro Bank'},
                {'id':'ASNBNL21', 'name': 'ASN Bank'},
                {'id':'FRBKNL2L', 'name': 'Friesland Bank'},
                {'id':'INGBNL2A', 'name': 'ING Bank'},
                {'id':'KNABNL2H', 'name': 'Knab'},
                {'id':'FVLBNL22', 'name': 'van Lanschot Bankiers'},
                {'id':'RABONL2U', 'name': 'Rabobank'},
                {'id':'RBRBNL21', 'name': 'Regio Bank'},
                {'id':'TRIONL2U', 'name': 'Triodos Bank'},
                {'id':'SNSBNL2A', 'name': 'SNS Bank'},
            ];
        }
    }.property(),

    isIdeal: Em.computed.equal('redirectPaymentMethod', 'IDEAL'),

    displayPaymentError: function() {
        this.get('controllers.currentOrder').setProperties({
            display_message: true,
            isError: true,
            autoHideMessage: false,
            message_content: 'There was an error sending you to the payment provider. Please try again.'
        });
       this.transitionToRoute('paymentProfile');
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
                    if (json.payment_url) {
                        var url = json.payment_url;
                        if (controller.get('redirectPaymentMethod')) {
                            url += '&default_pm=' + controller.get('redirectPaymentMethod');
                            if (controller.get('idealIssuerId')) {
                                url += '&ideal_issuer_id=' + controller.get('idealIssuerId');
                                url += '&default_act=true';
                            }
                        }
                        window.location =  url;
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
                        if (donation.get('tempRecurringAmount') === 0) {
                            // Delete donations set to 0.
                            donation.deleteRecord();
                            donation.save();
                        } else {
                            // Update donation when amount is greater than 0.
                            controller.get('controllers.currentOrderDonationList').updateDonation(donation, donation.get('tempRecurringAmount'));
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
            transitionToThanks(controller);
        });
        recurringDirectDebitPayment.one('didUpdate', function(record) {
            // FIXME: turn off didCreate, becameInvalid
            transitionToThanks(controller);
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
    needs: ['paymentProfile'],
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
        if (this.get('donationType') === '') {
            if (this.get('recurring')) {
                this.set('donationType', 'monthly');
            } else {
                this.set('donationType', 'single');
            }
        }
    }.observes('model'),

    // FIXME Implement a better way to handle vouchers and donations in the order.
    // Remove donations from voucher orders and remove vouchers from donations.
    // See: https://onepercentclub.atlassian.net/browse/BB-648
    removeDonationOrVouchers: function() {
        if (this.get('isVoucherOrder')) {
            var donations = this.get('donations');
            donations.forEach(function(donation) {
                donation.deleteRecord();
                donation.save();
            }, this);
        } else if (!this.get('isVoucherOrder')) {
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
        if (this.get('display_message')) {
            if (this.get('autoHideMessage')) {
                Ember.run.later(this, function() {
                    this.hideMessage();
                }, 10000);
            }
        }
    }).observes('display_message'),

    hideMessage: function() {
        this.set('display_message', false);
    },

    reloadOrderDetails: function() {
        var _this = this,
            profileRecord = _this.get('controllers.paymentProfile.model');

        // Reload order and payment profile after logging in
        // Check the order model is not already reloading
        if (this.get('model') && !this.get('isReloading') && this.get('currentUser.isLoaded')) {
            // set is-loading flash message with no timeout
            _this.send('setFlash', gettext('Reloading order details'), 'is-loading', false);

            // Attempt to reload the order and profile details
            this.get('model').reload().then( function (order) {
                // order reloaded successfully
                profileRecord.reload().then( function (profile) {
                    // profile reloaded successfully
                    _this.send('clearFlash');
                }, function (profile) {
                    // profile reload failed
                    _this.send('clearFlash');
                });
            }, function (order) {
                // order reload failed
                _this.send('clearFlash');
            });
        }
    }.observes('currentUser.isLoaded')
});


App.OrderThanksController = Em.ObjectController.extend({});


App.RecurringOrderThanksController = Em.ObjectController.extend({
    moreThanOneDonation: function() {
        return this.get('donations.length') > 1;
    }.property('length')
});


App.TickerController = Em.ArrayController.extend(Ember.SortableMixin, {
    sortProperties: ['created'],
    sortAscending: false,

    firstLoad: true,

    init: function(){
        this._super();
        var controller = this;
        $.getScript('/static/assets/js/vendor/audio-js.min.js');
        window.setTimeout(function(){
            controller.refresh();
        }, 5000);
    },

    play: function(file){
        var snd = window.audioJS({file: file});
        //var snd = new Sound(file);
        snd.play();

    },
    actions: {
        playSound: function(){
            var nr = Math.round(Math.random() * 5) + 1;
            var file = '/static/assets/media/new_donation' + nr  + '.wav';
            this.play(file);
        }
    },

    arrayContentWillChange: function(){
        if (!this.get('firstLoad')) {
            var nr = Math.round(Math.random() * 5) + 1;
            var file = '/static/assets/media/new_donation' + nr  + '.wav';
            this.play(file);
        }
    },

    refresh: function(){
        var controller = this;
        App.Ticker.find().then(function(){
            controller.set('firstLoad', false);
        });
        window.setTimeout(function(){
            console.log('reloading');
            controller.refresh();
        }, 20000);

    }


});
