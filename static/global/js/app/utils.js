App.Country = DS.Model.extend({
    url: 'utils/countries',
    title: DS.attr('string'),
    value: DS.attr('string')
});

App.CountrySelect = Em.Select.extend({
    content: App.Country.find(),
    optionValuePath: "content.value",
    optionLabelPath: "content.title"
})