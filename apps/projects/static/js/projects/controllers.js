App.MyProjectController.reopen({
    needs: ['application'],
    tabStory: Em.computed.equal('controllers.application.currentPath', 'myProject.story'),
    tabPitch: Em.computed.equal('controllers.application.currentPath', 'myProject.pitch'),
    tabBudget: Em.computed.equal('controllers.application.currentPath', 'myProject.goal')

});

App.MyProjectPitchController.reopen({
    nextStep: 'myProject.goal'
});

App.MyProjectGoalController = App.StandardTabController.extend({
    previousStep: 'myProject.pitch',
    nextStep: 'myProject.story',

    budgetLineNew: function(){
        return  App.MyProjectBudgetLine.createRecord();
    }.property(),

    canSave: function () {
		return !!this.get('model.title');
    }.property('model.title'),

    shouldSave: function(){
        // Determine if any part is dirty, project plan or any of the budget_lines
        if (this.get('isDirty')) {
            return true;
        }
        var budgetLines = this.get('budgetLines');
        var dirty = false;
        budgetLines.forEach(function(ad){
             if (ad.get('isDirty')) {
                 dirty = true;
             }

        });
        return dirty;
    }.property('isDirty', 'budgetLines.@each.isDirty'),

    // only show the budget errors if no budget was entered on the first display
    showBudgetError: function(){
        var validBudget = this.get('validBudget');
        var totalBudget = this.get('totalBudget');
        return (totalBudget && !validBudget);
    }.property('validBudget', 'totalBudget'),


    actions: {
        addBudgetLine: function(){
            console.log('adding line');
            var line = this.get('budgetLineNew');
            this.get('budgetLines').pushObject(line);
            line.save();
            // Create a new record for budgetLineNew
            this.set('budgetLineNew', App.MyProjectBudgetLine.createRecord());
        },

        removeBudgetLine: function(line){
            console.log('removing line');
            line.deleteRecord();
            line.save();
        }
    }
});

App.MyProjectStoryController.reopen({
    previousStep: 'myProject.goal',
    nextStep: 'myProject.organisation'
});

App.ProjectSupporterListController = Em.Controller.extend({
    needs: ['project'],

    supporters: function(){
        var project_id = this.get('controllers.project.id')
        return App.ProjectSupporter.find({project: project_id});
    }.property('controllers.project.id')
});

App.ProjectPlanController.reopen({
    hasPdfDownload: false
});

App.ProjectSearchFormController.reopen({
    orderedByNeeded: function(){
        return (this.get('ordering') == 'amount_needed');
    }.property('ordering')
});
