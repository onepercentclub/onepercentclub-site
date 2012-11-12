App.wallpostFormController = App.FormController.create({

});



App.WallpostFormView = Em.View.extend({
    contentBinding: 'App.wallpostFormController',
    templateName: 'wallpost_form',
    classNames: ['container', 'section'],
});
