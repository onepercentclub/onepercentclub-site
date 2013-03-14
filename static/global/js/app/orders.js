/*
 Models
 */

App.Order = DS.Model.extend({
    url: 'fund/orders',

    status: DS.attr('string'),
    recurring: DS.attr('string'),
    payment_method_id: DS.attr('string'),
    payment_submethod_id: DS.attr('string'),
    payment_methods: DS.hasMany('App.PaymentMethod'),
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
    order: DS.belongsTo('App.Order')
});


/* Models with CurrentOrder relations and urls. */

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


/* Models related to payment. */

App.PaymentOrderProfile = DS.Model.extend({
    url: 'fund/paymentorderprofiles',

    order: DS.belongsTo('App.Order'),
    firstName: DS.attr('string'),
    lastName: DS.attr('string'),
    email: DS.attr('string'),
    street: DS.attr('string'),
    city: DS.attr('string'),
    country: DS.attr('string'),
    postalCode: DS.attr('string')
});


App.PaymentMethod = DS.Model.extend({
    url: 'fund/paymentmethods',

    name: DS.attr('string'),
    order: DS.belongsTo('App.Order')
});


// TODO: Turn into ember Fixture??
// Maybe we can move this to the currentOrderController?
App.bankList = [
    Ember.Object.create({value:"0081", title: "Fortis"}),
    Ember.Object.create({value:"0021", title: "Rabobank"}),
    Ember.Object.create({value:"0721", title: "ING Bank"}),
    Ember.Object.create({value:"0751", title: "SNS Bank"}),
    Ember.Object.create({value:"0031", title: "ABN Amro Bank"}),
    Ember.Object.create({value:"0761", title: "ASN Bank"}),
    Ember.Object.create({value:"0771", title: "SNS Regio Bank"}),
    Ember.Object.create({value:"0511", title: "Triodos Bank"}),
    Ember.Object.create({value:"0091", title: "Friesland Bank"}),
    Ember.Object.create({value:"0161", title: "Van Lanschot Bankiers"})
];


//App.LatestDonation = App.OrderItem.extend({
//    url: 'fund/orders/latest/donations'
//});
//
//
//App.VoucherDonation = App.CurrentDonation.extend({
//   url: 'fund/vouchers/:code/donations'
//});


App.PaymentInfo = DS.Model.extend({
    url: 'fund/paymentinfo',

    payment_method: DS.attr('number'),
    amount: DS.attr('number'),
    firstName: DS.attr('string'),
    lastName: DS.attr('string'),
    address: DS.attr('string'),
    city: DS.attr('string'),
    country: DS.attr('string'),
    zipCode: DS.attr('string'),
    payment_url: DS.attr('string')
});


App.PaymentMethodInfo = DS.Model.extend({
    url: 'fund/paymentmethodinfo',

    payment_url: DS.attr('string'),
    bank_account_number: DS.attr('string'),
    bank_account_name: DS.attr('string'),
    bank_account_city: DS.attr('string')
});


App.Payment = DS.Model.extend({
    url: 'fund/payments',

    payment_method: DS.attr('string'),
    amount: DS.attr('number'),
    status: DS.attr('string')
});


/*
 Controllers
 */

App.CurrentOrderDonationListController = Em.ArrayController.extend({
    // The CurrentOrderController is needed for the single / monthly radio buttons.
    needs: ['currentOrder'],

    total: function() {
        return this.get('model').getEach('amount').reduce(function(accum, item) {
            // Use parseInt like this so we don't have a temporary string concatenation briefly displaying in the UI.
            return parseInt(accum) + parseInt(item);
        }, 0);
    }.property('model.@each.amount', 'model.length')
});


App.CurrentOrderDonationController = Em.ObjectController.extend({
    updateDonation: function(newAmount) {
        var donation = this.get('model');
        var transaction = this.get('store').transaction();
        transaction.add(donation);
        donation.set('amount', newAmount);
        transaction.commit();
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
    },

    neededAfterDonation: function() {
        return this.get('project.money_needed') - this.get('amount');
    }.property('amount', 'project.money_needed')
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
        this.set('model', voucher);
        this.set('transaction', transaction);
    },

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


App.PaymentOrderProfileController = Em.ObjectController.extend({
    initTransaction: function() {
        var transaction = this.get('store').transaction();
        this.set('transaction', transaction);
        transaction.add(this.get('content'));
    }.observes('content'),

    updateProfile: function() {
        var profile = this.get('content');
        var controller = this;
        // We should at least have an email address
        if (!profile.get('isDirty') && profile.get('email')) {
            // No changes. No need to commit.
            controller.transitionToRoute('currentPaymentMethodInfo');
        }
        this.get('transaction').commit();
        profile.on('didUpdate', function(record) {
            controller.transitionToRoute('currentPaymentMethodInfo');
        });
        // TODO: Validate data and return errors here
        profile.on('becameInvalid', function(record) {
            controller.get('content').set('errors', record.get('errors'));
        });
    }
});


App.CurrentOrderController = Em.ObjectController.extend({
    isIdeal: function() {
        return (this.get('content.payment_method_id') == 'dd-ideal');
    }.property('content.payment_method_id'),

    isDirectDebit: function() {
        return (this.get('content.payment_method_id') == 'dd-direct-debit');
    }.property('content.payment_method_id'),

//    initTransaction: function() {
//        var order = this.get('content');
//        var transaction = App.get('store').transaction();
//        this.set('transaction', transaction);
//        transaction.add(order);
//    }.observes('content'),

//    updateOrder: function() {
//        if (this.get('content.isDirty')) {
//            var controller = this;
//            var order = this.get('content');
//            this.get('transaction').commit();
//            order.on('didUpdate', function(record){
//                // Init a new private transaction.
//                controller.initTransaction();
//            });
//        }
//    }.observes('content.isDirty'),

//    updateOrder: function() {
//        var order = this.get('model');
//        var transaction = App.get('store').transaction();
//        transaction.add(order);
//        transaction.commit();
//        order.on('didUpdate', function(record){
//            console.log("blah")
//            transaction.removeCleanRecords()
//        });
//    }.observes('recurring'),

});


App.CurrentOrderPaymentController = Em.ObjectController.extend({
    contentBinding: App.CurrentOrderController.content
});


/*
 Views
 */

App.CurrentOrderView = Em.View.extend({
    templateName: 'current_order'
});


App.PaymentOrderProfileView = Em.View.extend({
    templateName: 'payment_order_profile',
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
    }
});


App.CurrentOrderVoucherListView = Em.View.extend({
    templateName: 'current_order_voucher_list',
    tagName: 'div',
    classNames: ['content']
});


App.FinalOrderItemListView = Em.View.extend({
    templateName: 'final_order_item_list',
    tagName: 'div'
});


App.CurrentOrderDonationView = Em.View.extend({
    templateName: 'current_order_donation',
    tagName: 'li',
    classNames: 'donation-project',

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


App.CurrentOrderPaymentView = Em.View.extend({
    tagName: 'div',
    classNames: ['content'],
    templateName: 'order_payment'
});


App.CurrentPaymentMethodInfoView = Em.View.extend({
    tagName: 'div',
    templateName: 'payment_method_info'
});


App.IdealPaymentMethodInfoView = Em.View.extend({
    tagName: 'form',
    templateName: 'ideal_payment_method_info',

    submit: function(e) {
        e.preventDefault();
    }
});


App.DirectDebitPaymentMethodInfoView = Em.View.extend({
    tagName: 'form',
    templateName: 'direct_debit_payment_method_info',

    submit: function(e){
        e.preventDefault();
    }
});

