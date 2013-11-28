App.FundRaiserView = Em.View.extend({
    templateName: 'fundRaiser'
});


App.FundRaiserNewView = Em.View.extend({
    templateName: 'fundraiser_new'
});


App.FundRaiserEditView = Em.View.extend({
    templateName: 'fundraiser_edit'
});


App.ProjectFundRaiserListView = Em.View.extend({
    templateName: 'project_fundraiser_list'
});

App.ProjectFundRaiserPopupView = Em.View.extend({
    templateName : 'project_fundraiser_popup'
});

App.ProjectFundRaiserView = Em.View.extend({
	templateName: 'project_fundraiser',

    tagName: 'li',
    didInsertElement: function(){
        var model = this.get('controller.content');
        var controller = this.get('controller');
        this.$('span').popover({
            trigger: 'hover',
            placement: 'top',
            title: model.get('title'),
            html : true,
            content : function(el){
                var contentView = App.ProjectFundRaiserPopupView.create({controller: controller});
                var html = contentView.renderToBuffer().buffer;
                return html;
            }
        });
    }
})


App.FundRaiserDonationListView = Em.View.extend({
    templateName: 'fundraiser_donation_list'
});

// TODO: Unused at this time.
//App.MyFundRaiserListView = Em.View.extend({
//    templateName: 'my_fund_raiser_list'
//});
//
//
//App.MyFundRaiserView = Em.View.extend({
//    templateName: 'my_fund_raiser'
//});
