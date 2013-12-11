/**
 * Router Map
 */


App.Router.map(function() {

    this.resource('voucher', {path: '/giftcards'}, function() {
        this.resource('voucherRedeem', {path: '/redeem/:code'});
    });
});





/**
 * Current Order Routes
 */

// Redirect to the donations list if somebody tries load '/support'.
App.VoucherRedeemRoute = Em.Route.extend({
    model: function(params){
        return App.Voucher.find(params.code);
    }
});

