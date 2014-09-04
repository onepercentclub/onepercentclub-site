App.PartnerView = Em.View.extend({
    templateName: 'partner'
});

App.PartnerIndexView = Em.View.extend({

    // Use a different template for Cheetah Fund.
    templateName: function (a, b) {
        var slug = this.get('controller.id');
        if (!slug) return 'partner_index';
        
        return slug + '/index';
    }.property('controller.id'),

    // Rerender the view if the template name changes.
    _templateNameChanged: function() {
        this.rerender();
    }.observes('templateName')
});

App.PartnerProjectsView = Em.View.extend({
    templateName: 'partner_projects',

    didInsertElement: function() {
        var _this = this;
        $(window).bind('scroll', function() {
            _this.didScroll();
        });
    },

    didScroll: function() {
        if(this.isScrolledToBottom()) {
            var amountLoadedCampaigns = $('.campaign-item').length,
                totalCampaigns = this.get('controller.amountProjects');

            if (amountLoadedCampaigns === totalCampaigns) return;
            this.incrementProperty('controller.projectNumber', 3);
        }
    },

    isScrolledToBottom: function() {
        var distanceTop = $(document).height() - $(window).height(),
            top = $(document).scrollTop();
            $('.campaign-item').addClass('is-shake');

        return top === distanceTop;
    }
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
});

