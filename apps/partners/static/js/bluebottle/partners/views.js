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

            if (_this.noMoreCampaign()) {
               $('.scroll-more-loader').removeClass('is-active'); 
            }
        });
    },

    noMoreCampaign: function() {
        var result = false,
            amountLoadedCampaigns = $('.campaign-item').length,
            totalCampaigns = this.get('controller.amountProjects');

        if (amountLoadedCampaigns === totalCampaigns) {
            return result = true;
        }
    },

    campaignLeft: function() {
        var amountLoadedCampaigns = $('.campaign-item').length,
            totalCampaigns = this.get('controller.amountProjects'),
            result = totalCampaigns - amountLoadedCampaigns;

            if (result > 6) {
                result = 6;
            } else {
                result = totalCampaigns - amountLoadedCampaigns;
            }

            return result;
    },

    didScroll: function() {
        var nthChild = this.campaignLeft();

        if(this.isScrolledToBottom()) {
            if (this.noMoreCampaign()) {
                $('.scroll-more-loader').removeClass('is-active');
                return;
            }
            this.incrementProperty('controller.projectNumber', 6);
            setTimeout(function() {
                $('.is-search:nth-last-of-type(-n + ' + ' ' + nthChild + ')').addClass('is-shake');
            });
            $('.scroll-more-loader').addClass('is-active');
        }
    },

    isScrolledToBottom: function() {
        var distanceTop = $(document).height() - $(window).height(),
            top = $(document).scrollTop();
            //$('.campaign-item:nth-last-of-type(-n + 3)').addClass('is-shake');

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

