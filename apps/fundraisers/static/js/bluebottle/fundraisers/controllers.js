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


App.FundRaiserWallPostListController = Em.ArrayController.extend({
    needs: ['fundRaiser'],
    perPage: 5,
    page: 1,

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
            App.WallPost.find({'content_type': 'fund raiser', 'content_id': id, page: page}).then(function(items){
                controller.get('model').pushObjects(items.toArray());
            });
        }
    }
});