/**
 * Router Map
 */

App.Router.map(function() {

    this.resource('currentOrder', {path: '/support'}, function() {
        this.route('donationList', {path: '/donations'});
        this.route('voucherList', {path: '/giftcards'});
        this.resource('paymentProfile', {path: '/details'});
        this.resource('paymentSignup', {path: '/signup'});
        this.resource('paymentSelect', {path: '/payment'}, function() {
            this.route('paymentError', {path: '/error'});
        });
    });

    this.resource('orderThanks', {path: '/support/thanks/:order_id'});
    this.resource('recurringOrderThanks', {path: '/support/monthly/thanks'});

    this.resource('ticker', {path: '/latest-donations'});

});

// Routes used in the Order Flow should use this class so that
// the orderFlowActive property will be set / unset on the main
// CurrentOrderRoute.
App.OrderFlowRoute = Em.Route.extend({
    activate: function () {
        this.setActive(true);
    },

    deactivate: function () {
        this.setActive(false);
    },

    setActive: function (active) {
        // FIXME: We shouldn't be referring to a specific controller from multiple routes.
        //        Would be better to set the property a parent route... maybe. Needs more work.
        var currentOrderController = this.container.lookup('controller:currentOrder');
        currentOrderController.set('orderFlowActive', active);
    }
});

/**
 * Current Order Routes
 */

// Redirect to the donations list if somebody tries load '/support'.
App.CurrentOrderIndexRoute = Em.Route.extend({
    redirect: function() {
        this.transitionTo('currentOrder.donationList');
    }
});


App.CurrentOrderRoute = App.OrderFlowRoute.extend({
    model: function(params) {
        return App.CurrentOrder.find('current');
    },
});


App.CurrentOrderDonationListRoute = App.OrderFlowRoute.extend(App.TrackRouteActivateMixin, App.ScrollToTop, {
    trackEventName: 'Donation list',

    model: function(params) {
        return this.modelFor('currentOrder').get('donations');
    },

    setupController: function(controller, donations) {
        this._super(controller, donations);
        this.controllerFor('currentOrder').set('isVoucherOrder', false);
        controller.set('paymentProfile', App.PaymentProfile.find('current'));
    }
});


App.CurrentOrderVoucherListRoute = App.OrderFlowRoute.extend({
    model: function(params) {
        var order = this.modelFor('currentOrder');
        return order.get('vouchers');
    },

    setupController: function(controller, vouchers) {
        this._super(controller, vouchers);
        this.controllerFor('currentOrder').set('isVoucherOrder', true);
    }
});


App.OrderThanksRoute = App.OrderFlowRoute.extend({

    googleConversion: {
        label: 'luszCIr_6wsQ7o7O1gM'
    },

    model: function(params) {
        var route = this;
        var order = App.Order.find(params.order_id);
        order.one('becameError', function() {
            route.replaceWith('home');
        });

        order.one("didLoad", function(){

            if (route.get('tracker')) {
                var tracker = route.get('tracker');
                tracker.trackEvent("Successful donation", {amount: this.get('total') });
                tracker.peopleIncrement('number_of_donations');
                tracker.peopleIncrement('total_donations_amount', this.get('total'));
            }

        });


        return order;
    }

});


/**
 * Payment for Current Order Routes
 */

App.PaymentProfileRoute = App.OrderFlowRoute.extend(App.TrackRouteActivateMixin, {
    trackEventName: 'Payment details',

    beforeModel: function() {
        var order = this.modelFor('currentOrder');
        if (order.get('isVoucherOrder')) {
            if (order.get('vouchers.length') <= 0 ) {
                this.transitionTo('currentOrder.voucherList');
            }
        } else {
            var controller = this.controllerFor('currentOrderDonationList');
            if (controller.get('editingRecurringOrder')) {
                if (controller.get('recurringTotal') === 0 && this.get('recurringTotal') == controller.get('recurringOrder.total')) {
                    this.transitionTo('currentOrder.donationList');
                }
            } else {
                if (!order.get('recurring') && order.get('donations.length') <= 0 ) {
                    this.transitionTo('currentOrder.donationList');
                }
            }
        }

    },

    model: function(params) {
        return App.PaymentProfile.find('current');
    }
});


App.PaymentSignupRoute = App.OrderFlowRoute.extend(App.TrackRouteActivateMixin, {
    trackEventName: 'Payment Signup',

    redirect: function(){
        var route = this;
        App.CurrentUser.find('current').then(function(user) {
            route.transitionTo('paymentSelect');
        });
    },
    model: function(params) {
        var model = App.UserCreate.createRecord();
        return App.PaymentProfile.find('current').then(function(profile){
            model.set('email', profile.get('email'));
            model.set('first_name', profile.get('firstName'));
            model.set('last_name', profile.get('lastName'));
            return model;
        });
    }
});


App.PaymentSelectRoute = App.OrderFlowRoute.extend(App.TrackRouteActivateMixin, {
    trackEventName: 'Payment select',

    beforeModel: function() {
        // var paymentProfile = this.modelFor('paymentProfile');
        var route = this;
        App.PaymentProfile.find('current').then(function(paymentProfile){
            if (!paymentProfile.get('isComplete')) {
                route.replaceWith('paymentProfile');
            }
        });
    },

    model: function(params) {
        return App.Payment.find('current');
    },
    setupController: function(controller, model){
        this._super(controller, model);
        controller.set('paymentProfile', App.PaymentProfile.find('current'));
    }
});


App.PaymentSelectPaymentErrorRoute = App.OrderFlowRoute.extend(App.TrackRouteActivateMixin, {
    trackEventName: 'Payment Error',

    beforeModel: function() {
        var order = this.modelFor('currentOrder');
        this.replaceWith('currentOrder.donationList');
        this.controllerFor('currentOrder').setProperties({
            display_message: true,
            isError: true,
            autoHideMessage: false,
            message_content: gettext('There was an error with your payment. Please try again.')
        });

    }
});


App.RecurringDirectDebitPaymentRoute = App.OrderFlowRoute.extend({
    beforeModel: function() {
        var order = this.modelFor('currentOrder');
        if (!order.get('recurring')) {
            this.transitionTo('paymentSelect');
        }
    },

    model: function() {
        var route = this;
        return App.RecurringDirectDebitPayment.find({}).then(function(recordList) {
                var store = route.get('store');
                if (recordList.get('length') > 0) {
                    var record = recordList.objectAt(0);
                    return record;
                } else {
                    return store.createRecord(App.RecurringDirectDebitPayment);
                }
            }
        );
    }
});


// Show the latest donations
App.TickerRoute = Em.Route.extend({
    model: function(params) {
        return  App.Ticker.find();
    }
});


App.RecurringOrderThanksRoute = App.OrderFlowRoute.extend(App.TrackRouteActivateMixin, {
    trackEventName: 'Successful Recurring Donation'
});