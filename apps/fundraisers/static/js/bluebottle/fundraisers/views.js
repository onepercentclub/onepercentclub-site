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

    html: function(){
        /* Unfortunately using templates isn't working when you enter the page a second time. Needs work!
        var controller = this.get('controller');
        var contentView = App.ProjectFundRaiserPopupView.create({controller: controller});
        return contentView.renderToBuffer().buffer;
        */
        var model= this.get('controller');
        return '<h3>' + model.get('model.owner.full_name') + '</h3>' +
                '<img src="' + model.get('model.image.small') +  '" />' +
                '<div class="project-fund-amount">' +
                '<strong class="amount-donated">&euro;' + model.get('model.amount_donated') + '</strong> ' +
                gettext('of') + ' <strong class="amount-asked">&euro;' + model.get('model.amount') + '</strong> ' +
                gettext('raised') + '</div>';

    }.property('controller.title'),

    tagName: 'li',
    didInsertElement: function(){
        var model = this.get('controller.content');
        this.$('img').popover({
            trigger: 'hover',
            placement: 'top',
            title: model.get('title'),
            html: true,
            content: this.get('html')
        });
    }
})

App.FundRaiserDeadLineDatePicker = App.DatePicker.extend({
    config: {minDate: 0, maxDate: "+6M"}
});


App.FundRaiserDonationListView = Em.View.extend({
    templateName: 'fundraiser_donation_list'
});

App.MyFundRaiserListView = Em.View.extend({
    templateName: 'my_fundraiser_list'
});
//
//
// TODO: Unused at this time.
//App.MyFundRaiserView = Em.View.extend({
//    templateName: 'my_fund_raiser'
//});
