/**
 * Voucher Models.
 * Vouchers are typically GiftCards
 *
 */

App.Voucher =  DS.Model.extend({
    url: 'vouchers',

    receiver_name: DS.attr('string', {defaultValue: ''}),
    receiver_email: DS.attr('string'),
    sender_name: DS.attr('string', {defaultValue: ''}),
    sender_email: DS.attr('string'),
    message: DS.attr('string', {defaultValue: ''}),
    language: DS.attr('string', {defaultValue: 'en'}),
    amount: DS.attr('number', {defaultValue: 25}),
    status: DS.attr('string'),

    donations: DS.hasMany('App.VoucherDonation')

});


// Add Voucher to Donation
App.Donation.reopen({
    voucher: DS.belongsTo('App.Voucher')
});


App.CurrentOrderVoucher = App.Voucher.extend({
    url: 'fund/orders/current/vouchers',

    order: DS.belongsTo('App.CurrentOrder')
});
