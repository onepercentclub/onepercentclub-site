App.LoginController.reopen(App.AuthJwtMixin, {
    loginTitle: gettext('Welcome!'),

    willClose: function () {
        this._super();

        // Also clear any FB login errors
        FBApp.set('connectError', null);
    }
});