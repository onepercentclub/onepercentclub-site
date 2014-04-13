App.MyProjectPitchController.reopen({
    nextStep: 'myProject.goal'
});

App.MyProjectGoalController = App.StandardTabController.extend({
    previousStep: 'myProject.pitch',
    nextStep: 'myProject.story',

    canSave: function () {
		return !!this.get('model.title');
    }.property('model.title')
});

App.MyProjectStoryController.reopen({
    previousStep: 'myProject.goal'
});

