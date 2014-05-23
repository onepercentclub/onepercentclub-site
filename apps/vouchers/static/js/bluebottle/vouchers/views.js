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