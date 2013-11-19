App.FundRaiserView = Em.View.extend({
    templateName: 'fund_raiser'

});


App.MyFundRaiserListView = Em.View.extend({
    templateName: 'my_fund_raiser_list'
});


App.MyFundRaiserNewView = Em.View.extend({
    templateName: 'my_fund_raiser_new'
});


App.MyFundRaiserView = Em.View.extend({
    templateName: 'my_fund_raiser'
});

App.ProjectFundRaiserListView = Em.View.extend({
    templateName: 'project_fundraiser_list'
});

App.ProjectFundRaiserView = Em.View.extend({
	templateName: 'project_fundraiser',
    tagName: 'li',
    didInsertElement: function(){
        this.$('a').popover({trigger: 'hover', placement: 'top', width: '300px'});
    }
})