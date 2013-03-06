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

    // Model fields
    // FIXME Make the drf2 serializer use the id (or slug) to serialize DS.belongsTo.
    //       This will enable us to remove the project_slug field.
    project: DS.belongsTo('App.Project'),
    project_slug: DS.attr('string'),
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

    vouchers: DS.hasMany('App.CurrentVoucher'),
    donations: DS.hasMany('App.CurrentDonation')
});

App.CurrentDonation = App.Donation.extend({
    url: 'fund/orders/current/donations',

    order: DS.belongsTo('App.CurrentOrder')
});

App.CurrentVoucher = App.Voucher.extend({
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


App.CustomVoucherRequest = DS.Model.extend({
    url: 'fund/customvouchers',

    amount: DS.attr('number', {defaultValue: 100}),
    type: DS.attr('string', {defaultValue: 'unknown'}),
    contact_name: DS.attr('string', {defaultValue: ''}),
    contact_email: DS.attr('string', {defaultValue: ''}),
    contact_phone: DS.attr('string', {defaultValue: ''}),
    organization: DS.attr('string', {defaultValue: ''}),
    message: DS.attr('string', {defaultValue: ''})
});


/*
 Controllers
 */

App.CurrentOrderDonationListController = Em.ArrayController.extend({
    // The CurrentOrderController is needed for the single / monthly radio buttons.
    needs: ['currentOrder']
});


App.CurrentOrderDonationController = Em.ObjectController.extend(App.UpdateDeleteMixin, {
    needs: ['currentOrder'],

    getTransaction: function(sender, key){
        var transaction =  this.get('controllers.currentOrder').getTransaction();
        if (!this.get('model.isLoaded')) {
            transaction.add(this.get('model'));
        }
        return transaction;
    }.observes('model.isLoaded'),


    updateDonation: function(newAmount) {
        this.get('model').set('amount', parseInt(newAmount));
        this.updateRecordOnServer();
    },

    deleteRecord: function(){
        var model = this.get('model');
        // TODO: note
        var order = App.CurrentOrder.find('current');
        order.get('donations').removeObject(model);
        return this.deleteRecordOnServer();
    },

    neededAfterDonation: function() {
        return this.get('project.money_needed_natural') - this.get('amount');
    }.property('amount', 'project.money_needed_natural')
});


App.CurrentOrderVoucherListController = Em.ArrayController.extend({
    count: function(){
        return this.get('content.length') - 1;
    }.property('content.length'),

    // TODO Use forEach like in the peepCode video.
    amount: function(){
        // Calculate the total amount of Vouchers that are added to the list, not the one that's being edited in the form.
        var amount = 0;
        this.forEach(function(item){
            if (! item.get('isDirty')) {
                amount += item.get('amount');
            }
        });
        return amount;
    }.property('content.length'),

    deleteOrderItem: function(item) {
        var transaction = App.store.transaction();
        transaction.add(item);
        item.deleteRecord();
        transaction.commit();
    }
});


App.CurrentOrderVoucherAddController = Em.ObjectController.extend({
    createNewVoucher: function() {
        var transaction = App.store.transaction();
        var voucher =  transaction.createRecord(App.CurrentVoucher);
        voucher.set('sender_name', App.userController.get('content.full_name'));
        voucher.set('sender_email', App.userController.get('content.email'));
        this.set('content', voucher);
        this.set('transaction', transaction);
    },

    addVoucher: function() {
        var voucher = this.get('content');
        var controller = this;
        voucher.on('didCreate', function(record) {
            controller.createNewVoucher();
            controller.set('content.sender_name', record.get('sender_name'));
            controller.set('content.sender_email', record.get('sender_email'));
        });
        voucher.on('becameInvalid', function(record) {
            controller.get('content').set('errors', record.get('errors'));
        });
        this.get('transaction').commit();
    }
});


App.PaymentOrderProfileController = Em.ObjectController.extend({
    initTransaction: function() {
        var transaction = App.store.transaction();
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


App.CurrentOrderController = Em.ObjectController.extend(App.UpdateModelMixin, {
    isIdeal: function() {
        return (this.get('content.payment_method_id') == 'dd-ideal');
    }.property('content.payment_method_id'),

    isDirectDebit: function() {
        return (this.get('content.payment_method_id') == 'dd-direct-debit');
    }.property('content.payment_method_id'),

    amount: function(){
        var amount = this.get('donations').getEach('amount').reduce(function(accum, item){
            return parseInt(accum + item);
        }, 0);
        amount += this.get('vouchers').getEach('amount').reduce(function(accum, item){
            return parseInt(accum + item);
        }, 0);
        return parseInt(amount);
    }.property('donations.@each.amount', 'vouchers.@each.amount'),


    updateOrder: function(){
        if (this.get('model.isDirty')) {
            this.updateRecordOnServer();
        }
    }.observes('model.isDirty')

});


App.CurrentOrderPaymentController = Em.ObjectController.extend({
    needs: ['currentOrder']

});


App.VoucherRedeemController = Em.ArrayController.extend({
    code: "",

    error: function(){
        if (this.get('voucher.isLoaded')) {
            // we don't get the code from the server, but store it here for future reference.
            this.set('voucher.code', this.get('code'));
            return false;
        }
        if (this.get('voucher')) {
            return true;
        }
        return false;
    }.property('voucher.isSaving', 'voucher.isLoaded'),

    submitVoucherCode: function() {
        var code = this.get('code');
        if (code) {
            var voucher = App.Voucher.find(code);
            this.set('voucher', voucher);

        }
    },

    redeemVoucher: function() {
        var controller = this;
        var voucher = this.get('voucher');
        var transaction = App.store.transaction();
        transaction.add(voucher);
        voucher.set('status', 'cashed');
        voucher.on('didUpdate',function(){
            controller.transitionToRoute('voucherRedeemDone');
        });
        transaction.commit();
    },

    // Currently not used. Keep this around for multiple Donations per Voucher.
    deleteVoucherDonation: function(orderItem) {
        var transaction = App.store.transaction();
        transaction.add(orderItem);
        orderItem.deleteRecord();
        transaction.commit();
    }
});


App.CustomVoucherRequestController = Em.ObjectController.extend({
    init: function() {
        this._super();
        this.createCustomVoucherRequest();
    },

    createCustomVoucherRequest: function() {
        var transaction = App.store.transaction();
        var voucherRequest =  transaction.createRecord(App.CustomVoucherRequest);
        voucherRequest.set('contact_name', App.userController.get('content.full_name'));
        voucherRequest.set('contact_email', App.userController.get('content.email'));
        this.set('content', voucherRequest);
        this.set('transaction', transaction);

    },

    sendRequest: function() {
        var transaction = this.get('transaction');
        var voucherRequest = this.get('content');
        transaction.commit();
    }
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

    submit: function(e){
        e.preventDefault();
        this.get('controller').updateProfile();
    }
});


App.CurrentOrderDonationListView = Em.View.extend({
    templateName: 'current_order_donation_list',
    tagName: 'form'
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

    change: function(e){
        this.get('controller').updateDonation(Em.get(e, 'target.value'));
    },

    delete: function(item) {
        var controller = this.get('controller');
        this.$().slideUp(500, function() {
            controller.deleteRecord();
        });
    }
});


App.CurrentOrderVoucherView = Em.View.extend({
    templateName: 'current_order_voucher',
    tagName: 'li',
    classNames: ['voucher-item'],

    delete: function() {
        var controller = this.get('controller');
        var item = this.get('content');
        this.$().slideUp(500, function(){controller.deleteOrderItem(item)});
    },

    submit: function(e) {
        e.preventDefault();
    }
});


App.CurrentOrderVoucherAddView = Em.View.extend({
    templateName: 'current_order_voucher_add',
    tagName: 'form',
    classNames: ['labeled']
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
    templateName: 'ideal_payment_method_info'
});


App.DirectDebitPaymentMethodInfoView = Em.View.extend({
    tagName: 'form',
    templateName: 'direct_debit_payment_method_info',

    submit: function(e){
        e.preventDefault();
    }
});


App.VoucherStartView = Em.View.extend({
    tagName: 'div',
    templateName: 'voucher_start'
});


App.VoucherRedeemView = Em.View.extend({
    tagName: 'div',
    templateName: 'voucher_redeem'
});


App.VoucherRedeemDoneView = Em.View.extend({
    tagName: 'div',
    templateName: 'voucher_redeem_done'
});


App.CustomVoucherRequestCustomView = Em.View.extend({
    tagName: 'form',
    templateName: 'custom_voucher_request'
});


App.VoucherDonationView = Em.View.extend({
    templateName: 'voucher_donation',
    tagName: 'li',
    classNames: 'donation-project',

    delete: function(item){
        var controller = this.get('controller');
        this.$().slideUp(500, function() {
            controller.deleteOrderItem(item)
        });
    }
});

