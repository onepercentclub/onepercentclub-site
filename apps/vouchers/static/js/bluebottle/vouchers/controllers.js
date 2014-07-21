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
    init: function() {
        this._super();
        this.createCustomVoucherRequest();
    },

    createCustomVoucherRequest: function() {
        var transaction = this.get('store').transaction();
        var voucherRequest =  transaction.createRecord(App.CustomVoucherRequest);
        voucherRequest.set('contact_name', this.get('currentUser.full_name'));
        voucherRequest.set('contact_email', this.get('currentUser.email'));
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