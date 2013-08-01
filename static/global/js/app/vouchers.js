/* Voucher stuff that not related to the payment order */


/* Models */

App.CustomVoucherRequest = DS.Model.extend({
    url: 'fund/customvouchers',

    number: DS.attr('number', {defaultValue: 100}),
    type: DS.attr('string', {defaultValue: 'unknown'}),
    contact_name: DS.attr('string', {defaultValue: ''}),
    contact_email: DS.attr('string', {defaultValue: ''}),
    contact_phone: DS.attr('string', {defaultValue: ''}),
    organization: DS.attr('string', {defaultValue: ''}),
    message: DS.attr('string', {defaultValue: ''})
});


App.VoucherDonation = App.Donation.extend({
    url: 'fund/vouchers/:code/donations',
    voucher: DS.belongsTo('App.Voucher')
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
        var transaction = this.get('store').transaction();
        transaction.add(voucher);
        voucher.set('status', 'cashed');
        voucher.on('didUpdate',function(){
            controller.transitionToRoute('voucherRedeemDone');
        });
        transaction.commit();
    },

    // Currently not used. Keep this around for multiple Donations per Voucher.
    deleteVoucherDonation: function(orderItem) {
        var transaction = this.get('store').transaction();
        transaction.add(orderItem);
        orderItem.deleteRecord();
        transaction.commit();
    }
});


App.CustomVoucherRequestController = Em.ObjectController.extend({
    needs: ['currentUser'],

    init: function() {
        this._super();
        this.createCustomVoucherRequest();
    },

    createCustomVoucherRequest: function() {
        var transaction = this.get('store').transaction();
        var voucherRequest =  transaction.createRecord(App.CustomVoucherRequest);
        voucherRequest.set('contact_name', this.get('controllers.currentUser.full_name'));
        voucherRequest.set('contact_email', this.get('controllers.currentUser.email'));
        var view = this;
        voucherRequest.on('didCreate',function(){
            view.transitionToRoute('customVoucherRequestDone');
        });
        this.set('content', voucherRequest);
        this.set('transaction', transaction);

    },

    sendRequest: function() {
        var transaction = this.get('transaction');
        var voucherRequest = this.get('content');
        transaction.commit();
    }
});


App.VoucherPickProjectController = Em.ArrayController.extend({
    // Because this hasn't got a Route we get the list over here
    init: function(){
        this._super();
        this.set('projects', App.Project.find({phase: 'campaign'}));
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


App.CustomVoucherRequestView = Em.View.extend({
    tagName: 'form',
    templateName: 'custom_voucher_request'
});


App.CustomVoucherRequestDoneView = Em.View.extend({
    templateName: 'custom_voucher_request_done'
});


App.VoucherDonationView = Em.View.extend({
    templateName: 'voucher_donation',
    tagName: 'li',
    classNames: 'donation-project control-group',

    neededAfterDonation: function () {
        return '';
    }.property('project', 'voucher'),

    'delete': function(item){
        var controller = this.get('controller');
        this.$().slideUp(500, function() {
            controller.deleteOrderItem(item)
        });
    }
});

App.VoucherPickProjectView = Em.View.extend({
    templateName: 'voucher_pick_project'
});

