App.MyProjectOrganisationController.reopen({
	previousStep: 'myProject.story',
    nextStep: 'myProject.bank'
});

App.MyProjectBankController.reopen({
    previousStep: 'myProject.organisation',
    nextStep: 'myProject.submit'
});

App.MyProjectSubmitController = App.StandardTabController.extend({
    needs: ['myProjectBank'],
    previousStep: 'myProject.bank'
});

