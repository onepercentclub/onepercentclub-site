App.FundRaiserIsOwner = Em.Mixin.create({
    needs: ['currentUser'],
    isOwner: function() {
        var username = this.get('controllers.currentUser.username');
        var ownername = this.get('model.owner.username');
        if (username) {
            return (username == ownername);
        }
        return false;
    }.property('model.owner', 'controllers.currentUser.username')
});


App.FundRaiserController = Em.ObjectController.extend(App.FundRaiserIsOwner, {
    needs: ['project']
});


App.FundRaiserNewController = Em.ObjectController.extend(App.Editable, App.FundRaiserIsOwner, {
    needs: ['project'],
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

            model.one('didUpdate', function(record) {
                controller.transitionToRoute('fundRaiser', record);
            });

            model.save();
        }
    }
});


App.FundRaiserEditController = App.FundRaiserNewController.extend({
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


App.FundRaiserDonationListController = Em.ObjectController.extend({
    needs: ['currentUser']
});
