App.AnimateProgressMixin = Em.Mixin.create({
    didInsertElement: function(){
        var donated = this.get('controller.campaign.money_donated');
        var asked = this.get('controller.campaign.money_asked');
        this.$('.slider-progress').css('width', '0px');
        var width = 0;
        if (asked > 0) {
            width = 100 * donated / asked;
            width += '%';
        }
        this.$('.slider-progress').animate({'width': width}, 1000);
    }
});

App.ProjectMembersView = Em.View.extend({
    templateName: 'project_members'
});

App.ProjectSupporterView = Em.View.extend({
    templateName: 'project_supporter',
    tagName: 'li',
    didInsertElement: function(){
        this.$('a').popover({trigger: 'hover', placement: 'top', width: '100px'})
    }
});


App.ProjectSupporterListView = Em.View.extend({
    templateName: 'project_supporter_list'
});


App.ProjectListView = Em.View.extend(App.ScrollInView, {
    templateName: 'project_list'
});

App.ProjectPreviewView = Em.View.extend(App.AnimateProgressMixin, {
    templateName: 'project_preview'
});


App.ProjectSearchFormView = Em.View.extend({
    templateName: 'project_search_form'
});


App.ProjectPlanView = Em.View.extend(App.ScrollInView, {
    templateName: 'project_plan',

    staticMap: function(){
        var latlng = this.get('controller.latitude') + ',' + this.get('controller.longitude');
        return "http://maps.googleapis.com/maps/api/staticmap?" + latlng + "&zoom=8&size=600x300&maptype=roadmap" +
            "&markers=color:pink%7Clabel:P%7C" + latlng + "&sensor=false";
    }.property('latitude', 'longitude')
});


App.ProjectView = Em.View.extend(App.AnimateProgressMixin, {
    templateName: 'project',

    didInsertElement: function(){
        this._super();
        this.$('.tags').popover({trigger: 'hover', placement: 'top', width: '100px'});
    }
});


/* Form Elements */

App.ProjectOrderList = [
    {value: 'title', title: gettext("title")},
    {value: 'money_needed', title: gettext("money needed")},
    {value: 'deadline', title: gettext("deadline")}
];

App.ProjectOrderSelectView = Em.Select.extend({
    content: App.ProjectOrderList,
    optionValuePath: "content.value",
    optionLabelPath: "content.title"
});

App.ProjectPhaseList = [
    {value: 'plan', title: gettext("Writing Plan")},
    {value: 'campaign', title: gettext("Campaign")},
    {value: 'act', title: gettext("Act")},
    {value: 'results', title: gettext("Results")},
    {value: 'realized', title: gettext("Realised")}
];

App.ProjectPhaseSelectView = Em.Select.extend({
    content: App.ProjectPhaseList,
    optionValuePath: "content.value",
    optionLabelPath: "content.title",
    prompt: gettext("Pick a phase")

});



/*
 Project Manage Views
 */


App.MyProjectListView = Em.View.extend({
    templateName: 'my_project_list'
});

App.MyProjectView = Em.View.extend({
    templateName: 'my_project'

});


// Project Pitch Phase

App.MyPitchNewView = Em.View.extend({
    templateName: 'my_pitch_new'
});

App.MyProjectPitchView = Em.View.extend({
    templateName: 'my_project_pitch'

});

App.MyProjectPitchIndexView = Em.View.extend({
    templateName: 'my_pitch_index'

});

App.MyProjectPitchBasicsView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_pitch_basics'
});

App.MyProjectPitchMediaView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_media'
});

App.MyProjectPitchLocationView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_location'
});


App.MyProjectPitchSubmitView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_pitch_submit'
});



// Project Plan phase

App.MyProjectPlanView = Em.View.extend({
    templateName: 'my_project_plan'
});

App.MyProjectPlanIndexView = Em.View.extend({
    templateName: 'my_project_plan_index'
});

App.MyProjectPlanBasicsView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_basics'
});

App.MyProjectPlanDescriptionView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_description'
});

App.MyProjectPlanLocationView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_location'
});

App.MyProjectPlanMediaView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_media'
});

App.MyProjectPlanOrganisationView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_organisation'
});

App.MyProjectPlanLegalView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_legal'
});

App.MyProjectPlanAmbassadorsView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_ambassadors'
});

App.MyProjectPlanBankView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_bank'
});

App.MyProjectPlanBudgetView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_budget'
});

App.MyProjectPlanCampaignView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_campaign'
});

App.MyProjectPlanSubmitView = Em.View.extend(App.PopOverMixin, {
    templateName: 'my_project_plan_submit'
});

