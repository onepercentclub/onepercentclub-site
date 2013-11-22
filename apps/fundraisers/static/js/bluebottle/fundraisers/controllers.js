//App.FundRaiserController = Em.ObjectController.extend({
//    needs: ['project']
//});


App.FundRaiserNewController = Em.ObjectController.extend(App.Editable, {
    needs: ['currentUser', 'project'],
    actions: {
        updateRecordOnServer: function(){
            var controller = this;
            var model = this.get('model');

            model.one('becameInvalid', function(record){
                model.set('errors', record.get('errors'));
            });

            model.one('didCreate', function(record){
                controller.transitionToRoute('fundRaiser', record);
            });

            model.save();
        }
    }
});

App.ProjectFundRaiserListController = Em.ArrayController.extend({
    needs: ['project'],
	fundraisersLoaded: function(sender, key) {
		if (this.get(key)) {
			this.set('model', this.get('fundraisers').toArray());
		} else {
			this.set('model', null);
		}
	}.observes('fundraisers.isLoaded')
});
