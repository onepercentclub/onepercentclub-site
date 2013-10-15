App.MonthlyOrderDonation = App.Donation.extend({
    url: 'fund/orders/current/donations',
    order: DS.belongsTo('App.Order')
});
