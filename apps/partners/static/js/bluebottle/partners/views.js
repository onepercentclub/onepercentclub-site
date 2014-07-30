App.PartnerView = Em.View.extend({

    // Use a different template for Cheetah Fund.
    templateName: function (a, b) {
        var slug = this.get('controller.id');
        var templateName = 'partner';
        if (slug === 'cheetah') {
            templateName = 'cheetah/index';
        }
        return templateName;
    }.property('controller.id'),

    // Rerender the view if the template name changes.
    _templateNameChanged: function() {
        this.rerender();
    }.observes('templateName')
});


App.CheetahQuizView = Em.View.extend({
    templateName: 'cheetah_quiz',

    keyUp: function(){
        var answer = $('.quiz-input').val(),
            removeComma = answer.split(','),
            newAnswer = removeComma[0].replace('.', '');

        $('.quiz-input').val(newAnswer)
    }
});

App.CheetahFaqView = Em.View.extend({
    didInsertElement: function(){
        this.$('.faq-question').on('click', function() {
            var test = $(this).toggleClass('active');
        });
    }
})