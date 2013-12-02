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


App.FundRaiserIndexController = Em.ArrayController.extend({
    needs: ['fundRaiser', 'currentUser'],
    perPage: 5,
    page: 1,

    isOwner: function(){
        var userName = this.get('controllers.currentUser.username');
        var ownerName = this.get('controllers.fundRaiser.owner.username');
        if (userName) {
            return (userName == ownerName);
        }
        return false;
    }.property('controllers.fundRaiser.owner', 'controllers.fundRaiser.owner.username'),

    remainingItemCount: function(){
        if (this.get('meta.total')) {
            return this.get('meta.total') - (this.get('page')  * this.get('perPage'));
        }
        return 0;
    }.property('page', 'perPage', 'meta.total'),

    canLoadMore: function(){
        var totalPages = Math.ceil(this.get('meta.total') / this.get('perPage'));
        return totalPages > this.get('page');
    }.property('perPage', 'page', 'meta.total'),

    actions: {
        showMore: function() {
            var controller = this;
            var page = this.incrementProperty('page');
            var id = this.get('controllers.fundRaiser.model.id');
            App.WallPost.find({'parent_type': 'fund raiser', 'parent_id': id, page: page}).then(function(items){
                controller.get('model').pushObjects(items.toArray());
            });
        }
    }
});


App.MyFundRaiserListController = Em.ArrayController.extend({
    needs: ['currentUser']
});
