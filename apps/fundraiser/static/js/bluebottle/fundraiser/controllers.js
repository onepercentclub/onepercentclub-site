App.FundRaiserController = Em.ObjectController.extend({
});


App.MyFundRaiserNewController = Em.ObjectController.extend(App.Editable, {
    needs: ['currentUser'],
    actions: {
        updateRecordOnServer: function(){
            var controller = this;
            var model = this.get('model');
            model.one('becameInvalid', function(record){
                model.set('errors', record.get('errors'));
            });

            model.one('didCreate', function(record){
                controller.transitionToRoute('myFundRaiser', record);
            });

            model.save();
        }
    }
});
