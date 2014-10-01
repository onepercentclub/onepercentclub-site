App.MpesaPayment = DS.Model.extend({
    url: 'mpesa/payments',

    project: DS.belongsTo('App.Project'),
    mpesa_name: DS.attr('string'),
    mpesa_phone: DS.attr('string'),
    date: DS.attr('date'),
    amount: DS.attr('number')

});