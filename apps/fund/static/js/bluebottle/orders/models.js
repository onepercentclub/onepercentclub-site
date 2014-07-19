/**
 * Models
 */

/**
 * Embedded objects
 */
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
App.Adapter.map('App.ProjectSupporter', {
    project: {embedded: 'load'},
    member: {embedded: 'load'}
});
App.Adapter.map('App.ProjectDonation', {
    member: {embedded: 'load'}
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


App.ProjectSupporter = DS.Model.extend({
    url: 'fund/project-supporters',

    project: DS.belongsTo('App.ProjectPreview'),
    fundraiser: DS.belongsTo('App.FundRaiser'),
    member: DS.belongsTo('App.UserPreview'),
    date_donated: DS.attr('date'),

    time_since: function(){
        return Globalize.format(this.get('date_donated'), 'X');
    }.property('date_donated')
});


App.ProjectDonation = DS.Model.extend({
    url: 'fund/project-donations',

    member: DS.belongsTo('App.UserPreview'),
    date_donated: DS.attr('date'),
    amount: DS.attr('number'),


    time_since: function(){
        return Globalize.format(this.get('date_donated'), 'X');
    }.property('date_donated')
});



App.Ticker = DS.Model.extend({
    url: 'fund/latest-donations',
    project: DS.belongsTo('App.ProjectPreview'),
    user: DS.belongsTo('App.UserPreview'),
    amount: DS.attr('number'),
    created: DS.attr('date')
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
    order: DS.belongsTo('App.CurrentOrder'),
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
    isComplete: Em.computed.and('firstName.length', 'lastName.length', 'email.length', 'address.length', 'postalCode.length', 'city.length', 'country.length')
});


App.Payment = DS.Model.extend({
    url: 'fund/payments',

    paymentMethod: DS.attr('string'),
    paymentSubmethod: DS.attr('string'),
    paymentUrl: DS.attr('string'),
    availablePaymentMethods: DS.attr('array')
});

