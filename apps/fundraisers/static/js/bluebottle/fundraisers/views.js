App.FundRaiserView = Em.View.extend({
    templateName: 'fundraiser'
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


App.ProjectFundRaiserView = Em.View.extend({
	templateName: 'project_fundraiser',
    tagName: 'li',
    didInsertElement: function(){
        this.$('span').popover({trigger: 'hover', placement: 'top', width: '300px'});
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
