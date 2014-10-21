App.Adapter.map('App.MonthlyDonation', {
    projects: {embedded: 'load'}
});

App.Adapter.map('App.MonthlyDonationProject', {
    //project: {embedded: 'load'}
});


App.MonthlyDonationProject = DS.Model.extend({
    url: 'monthly_donations/projects',
    project: DS.belongsTo('App.ProjectPreview'),
    donation: DS.belongsTo('App.MonthlyDonation')

});


App.MonthlyDonation = DS.Model.extend({
    url: 'monthly_donations',

    active: DS.attr('boolean', {defaultValue: false}),
    amount: DS.attr('number', {defaultValue: 20}),

    projects: DS.hasMany('App.MonthlyDonationProject'),

    name: DS.attr('string'),
    city: DS.attr('string'),
    country: DS.belongsTo('App.Country'),
    iban: DS.attr('string'),
    bic: DS.attr('string'),

    isIncomplete: function(){
        if (this.get('didError')) {
            return true;
        }
        if (this.get('isNew')) {
            return true;
        }
        if (this.get('name') && this.get('city') && this.get('iban') && this.get('bic')) {
            return false;
        }
        return true;
    }.property('name', 'city', 'iban', 'bic', 'isDirty')
});
