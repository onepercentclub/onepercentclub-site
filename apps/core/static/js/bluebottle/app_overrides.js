App.ApplicationController.reopen({
    needs: ['currentUser', 'currentOrder', 'myProjectList'],
});