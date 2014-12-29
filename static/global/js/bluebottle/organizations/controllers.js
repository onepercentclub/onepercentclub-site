App.MyProjectOrganisationController.reopen({
    previousStep: 'myProject.story',
    nextStep: 'myProject.bank'
});

App.MyProjectBankController.reopen({
    previousStep: 'myProject.organisation',
    nextStep: 'myProject.submit'
});

App.MyProjectSubmitController.reopen({
    needs: ['myProjectBank', 'myProjectOrganisation'],
    previousStep: 'myProject.bank'
});

