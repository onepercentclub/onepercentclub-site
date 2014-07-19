App.FundRaiserIsOwner = Em.Mixin.create({
    isOwner: function() {
        var username = this.get('currentUser.username');
        var ownername = this.get('model.owner.username');
        if (username) {
            return (username == ownername);
        }
        return false;
    }.property('model.owner', 'currentUser.username')
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


App.ProjectFundRaiserAllController = Em.ArrayController.extend({
    actions: {
        showFundraiser: function(fundraiser){
            $('.modal-close').click();
            this.transitionToRoute('fundRaiser', fundraiser);
        }
    }
});



App.ProjectFundRaiserListController = Em.ArrayController.extend({
    needs: ['project', 'projectFundRaiserAll'],

    fundraisers: function () {
        return App.FundRaiser.find({project: this.get('controllers.project.id')});
    }.property('controllers.project.id'),
    
	fundraisersLoaded: function(sender, key) {
		if (this.get(key)) {
			this.set('model', this.get('fundraisers').toArray());
		} else {
			this.set('model', null);
		}
	}.observes('fundraisers.isLoaded'),

    actions: {
        showAllFundraisers: function(project){
            // Get the controller or create one
            var controller = this.get('controllers.projectFundRaiserAll');
            controller.set('model', App.FundRaiser.find({project: project.get('id'), page_size: 200}));

            // Get the view. This should be defined.
            var view = App.ProjectFundRaiserAllView.create();
            view.set('controller', controller);

            var modalPaneTemplate = ['<div class="modal-wrapper"><a class="modal-close" rel="close">&times;</a>{{view view.bodyViewClass}}</div>'].join("\n");

            Bootstrap.ModalPane.popup({
                classNames: ['modal', 'large'],
                defaultTemplate: Em.Handlebars.compile(modalPaneTemplate),
                bodyViewClass: view,
                secondary: 'Close'
            });

        }
    }

});


App.FundRaiserDonationListController = Em.ObjectController.extend({});


App.FundRaiserSupporterListController = Em.ArrayController.extend({
    needs: ['fundRaiser'],

    supporters: function(){
        //var project_id = this.get('controllers.fundRaiser.project.id')
        var fundraiser_id = this.get('controllers.fundRaiser.id')
        //return App.ProjectSupporter.find({project: project_id});
        return App.ProjectSupporter.find({fundraiser: fundraiser_id});
    }.property('controllers.fundRaiser.id')


});

App.FundRaiserIndexController = Em.ArrayController.extend({
    needs: ['fundRaiser'],
    perPage: 5,
    page: 1,

    isOwner: function(){
        var userName = this.get('currentUser.username');
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


App.MyFundRaiserListController = Em.ArrayController.extend({});
