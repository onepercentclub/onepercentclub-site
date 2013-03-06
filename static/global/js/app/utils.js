App.Country = DS.Model.extend({
    url: 'utils/countries',
    title: DS.attr('string'),
    value: DS.attr('string')
});


App.CountrySelect = Em.Select.extend({
    content: App.Country.find(),
    optionValuePath: "content.value",
    optionLabelPath: "content.title"
});


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


App.TransactionMixin = Em.Mixin.create({
    getTransaction: function(sender, key){
        if (this.get('transaction') == 'defaultTransaction') {
            this.set('transaction', App.store.transaction());
        }
        if (this.get('model.isLoaded')) {
            this.get('transaction').add(this.get('model'));
        }
        return this.get('transaction');
    }.observes('model.isLoaded')
});


App.DeleteModelMixin = Em.Mixin.create(App.TransactionMixin, {
    deleteRecordOnServer: function(sender, key) {
        var model = this.get('model');
        model.deleteRecord();
        this.get('transaction').commit();
    }
});


App.UpdateModelMixin = Em.Mixin.create(App.TransactionMixin, {
    updateRecordOnServer: function(sender, key) {
        var model = this.get('model');
        this.get('transaction').commit();
    }
});

App.UpdateDeleteMixin = Em.Mixin.create(App.UpdateModelMixin, App.DeleteModelMixin);


/**
 * Change how Transaction is working. We will never use the defaultTransaction.
 * After a commit put all records that are in a transaction into a newly created transaction.
 *
 */
DS.Transaction.reopen({
    remove: function(record) {
        // Check if there's already a new transaction to move the records to or create one.
        if (typeof newTransaction === 'undefined') {
            newTransaction = this.get('store').transaction();
        }
        newTransaction.adoptRecord(record);
    }
});

