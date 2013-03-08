App.Country = DS.Model.extend({
    url: 'utils/countries',
    title: DS.attr('string'),
    value: DS.attr('string')
});

// FIXME: Ember data doesn't work this this:
//App.CountrySelect = Em.Select.extend({
//    content: App.Country.find(),
//    optionValuePath: "content.value",
//    optionLabelPath: "content.title"
//});


App.IsAuthorMixin = Em.Mixin.create({
    isAuthor: function() {
        var username = this.get('controllers.currentUser.username');
        var authorname = this.get('author.username');
        if (username) {
            return (username == authorname);
        }
        return false;
    }.property('author.username', 'controllers.currentUser.username')
});


App.DeleteModelMixin = Em.Mixin.create({
    deleteRecordOnServer: function() {
        var record = this.get('model');
        var transaction = this.get('store').transaction();
        transaction.add(record);
        record.deleteRecord();
        transaction.commit();
    }
});
