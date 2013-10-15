
/* Controllers */

App.ContactMessageController = Em.ObjectController.extend({
    needs: ['currentUser'],

    startEditing: function() {
        var record = this.get('model');
        if (record.transaction.isDefault == true) {
            this.transaction = this.get('store').transaction();
            this.transaction.add(record);
        }
    },

    updateRecordOnServer: function(){
        var controller = this;
        var model = this.get('model');
        model.one('becameInvalid', function(record){
            model.set('errors', record.get('errors'));
        });
        model.transaction.commit();
    },

    stopEditing: function() {
    }
});

