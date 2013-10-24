App.Adapter.map('App.RecurringOrder', {
    donations: {embedded: 'load'}
});


App.RecurringDirectDebitPayment = DS.Model.extend({
    url: 'fund/recurring/directdebitpayments',

    active: DS.attr('boolean', {defaultValue: false}),
    amount: DS.attr('number', {defaultValue: 20}),

    name: DS.attr('string'),
    city: DS.attr('string'),
    account: DS.attr('string'),

    isIncomplete: function(){
        if (this.get('didError')) {
            return true;
        }
        if (this.get('isNew')) {
            return true;
        }
        if (this.get('name') && this.get('city') && this.get('account')) {
            return false;
        }
        return true;
    }.property('name', 'city', 'account', 'isDirty')
});

App.RecurringOrder = App.Order.extend({
    url: 'fund/recurring/orders',
    donations: DS.hasMany('App.RecurringDonation'),

});

App.RecurringDonation = App.Donation.extend({
    url: 'fund/recurring/donations',
    order: DS.belongsTo('App.RecurringOrder')
});

