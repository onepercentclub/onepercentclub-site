/* Voucher stuff that not related to the payment order */


/* Models */

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


/* Controllers */

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
            controller.transitionTo('voucherRedeemDone');
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


/* Views */

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