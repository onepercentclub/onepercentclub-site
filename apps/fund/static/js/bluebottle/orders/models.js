/**
 * Models
 */

/**
 * Embedded objects
 */
App.Adapter.map('App.DonationPreview', {
    project: {embedded: 'both'},
    member: {embedded: 'both'}
});
App.Adapter.map('App.Order', {
    donations: {embedded: 'load'},
    vouchers: {embedded: 'load'}
});
App.Adapter.map('App.CurrentOrder', {
    donations: {embedded: 'load'},
    vouchers: {embedded: 'load'}
});
App.Adapter.map('App.Ticker', {
    project: {embedded: 'load'},
    user: {embedded: 'load'}
});


App.Order = DS.Model.extend({
    url: 'fund/orders',

    status: DS.attr('string'),
    recurring: DS.attr('boolean'),
    vouchers: DS.hasMany('App.Voucher'),
    donations: DS.hasMany('App.Donation'),
    created: DS.attr('date'),
    total: DS.attr('number')
});


App.Donation = DS.Model.extend({
    url: 'fund/donations',

    project: DS.belongsTo('App.Project'),
    fundraiser: DS.belongsTo('App.FundRaiser'),
    amount: DS.attr('number', {defaultValue: 20}),
    status: DS.attr('string'),
    type: DS.attr('string'),
    order: DS.belongsTo('App.Order')
});


App.Ticker = DS.Model.extend({
    url: 'fund/latest-donations',
    project: DS.belongsTo('App.ProjectPreview'),
    user: DS.belongsTo('App.UserPreview'),
    amount: DS.attr('number'),
    created: DS.attr('date')
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
    status: DS.attr('string'),

    order: DS.belongsTo('App.Order'),
    donations: DS.hasMany('App.VoucherDonation')

});


/* Models with CurrentOrder relations and urls. */

// FIXME Get rid of CurrentOrder models

App.CurrentOrder = App.Order.extend({
    url: 'fund/orders',

    vouchers: DS.hasMany('App.CurrentOrderVoucher'),
    donations: DS.hasMany('App.CurrentOrderDonation'),

    // This is a hack to work around an issue with Ember-Data keeping the id as 'current'.
    // App.UserSettingsModel.find(App.CurrentUser.find('current').get('id_for_ember'));
    id_for_ember: DS.attr('number')
});


App.CurrentOrderDonation = App.Donation.extend({
    url: 'fund/orders/current/donations',
    order: DS.belongsTo('App.CurrentOrder')
});


App.CurrentOrderVoucher = App.Voucher.extend({
    url: 'fund/orders/current/vouchers',

    order: DS.belongsTo('App.CurrentOrder')
});


/* Models related to payments. */

App.PaymentProfile = DS.Model.extend({
    url: 'fund/paymentprofiles',

    firstName: DS.attr('string'),
    lastName: DS.attr('string'),
    email: DS.attr('string'),
    address: DS.attr('string'),
    postalCode: DS.attr('string'),
    city: DS.attr('string'),
    country: DS.attr('string'),
    isComplete: function() {
        return !Em.isEmpty(this.get('firstName')) && !Em.isEmpty(this.get('lastName')) && !Em.isEmpty(this.get('email')) &&
               !Em.isEmpty(this.get('address')) && !Em.isEmpty(this.get('postalCode')) && !Em.isEmpty(this.get('city')) &&
               !Em.isEmpty(this.get('country'));
    }.property('firstName', 'lastName', 'email', 'address', 'postalCode', 'city', 'country')
});


App.Payment = DS.Model.extend({
    url: 'fund/payments',

    paymentMethod: DS.attr('string'),
    paymentSubmethod: DS.attr('string'),
    paymentUrl: DS.attr('string'),
    availablePaymentMethods: DS.attr('array')
});

