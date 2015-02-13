App.PartnerView = Em.View.extend({
    templateName: 'partner'
});

App.PartnerIndexView = Em.View.extend({

    // Use a different template for Cheetah Fund.
    templateName: function (a, b) {
        var slug = this.get('controller.id');
        if (slug == 'cheetah')  return 'cheetah/index';
        return 'partner_index';

    }.property('controller.id'),

    // Re-render the view if the template name changes.
    _templateNameChanged: function() {
        this.rerender();
    }.observes('templateName')
});

App.PartnerProjectsView = Em.View.extend({
    templateName: 'partner_projects',

    didInsertElement: function() {
        $(document).on('scroll', $.proxy(this.didScroll, this));
        $(document).on('touchmove', $.proxy(this.didScrollTouch, this));
    },

    willDestroyElement: function(){
        $(document).off('scroll', $.proxy(this.didScroll, this));
        $(document).off('touchmove', $.proxy(this.didScrollTouch, this));
    },

    noMoreCampaign: function() {
        var result = false,
            amountLoadedCampaigns = $('.campaign-item').length,
            totalCampaigns = this.get('controller.amountProjects');

        if (amountLoadedCampaigns === totalCampaigns) {
            return result = true;
        }
    }.observes('controller.amountProjects'),

    campaignLeft: function() {
        var amountLoadedCampaigns = $('.campaign-item').length,
            totalCampaigns = this.get('controller.amountProjects'),
            result = totalCampaigns - amountLoadedCampaigns;

            if (result > 3) {
                result = 3;
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
            this.incrementProperty('controller.projectNumber', 3);
            setTimeout(function() {
                $('.is-search:nth-last-of-type(-n + ' + ' ' + nthChild + ')').addClass('is-fadeIn');
            });
            $('.scroll-more-loader').addClass('is-active');

            if (this.noMoreCampaign()) {
               $('.scroll-more-loader').removeClass('is-active'); 
            }
        } else {
            $('.scroll-more-loader').removeClass('is-active');    
        }

    },

    didScrollTouch: function() {
        $('.click-more-loader').addClass('is-active');
        $('.scroll-more-loader').removeClass('is-active');

        if (this.noMoreCampaign()) {
            $('.click-more-loader').removeClass('is-active');
            $('.scroll-more-loader').removeClass('is-active');
        }
    },

    isScrolledToBottom: function() {
        var distanceTop = $(document).height() - $(window).height(),
            top = $(document).scrollTop();
        return top >= distanceTop;
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

App.BusinessInspiredView = Em.View.extend({
    templateName: 'inspired',

    setQuoteTimeout: function(element) {
        var _this = this;
        setInterval(function() {
            if (_this.$() === undefined) {
                return
            } else {
                _this.$().find(element).toggleClass('is-selected');
            }
            
        }, 12000);
    },

    didInsertElement: function() {
        var _this = this

        this.setQuoteTimeout('.business-slider');

        $('.quote-slider-item, .carousel-nav-item').on('click', function(){
            _this.$().find('.business-slider').toggleClass('is-selected');
        })
    }
});

App.BusinessView = Em.View.extend({
    didInsertElement: function() {
        _this = this;
        $('.corporate-menu li').on('click', function(){
            var thisElement = $(this), 
                newId = thisElement.find('a').data('id');

            $('.corporate-menu li').removeClass('is-active');
            thisElement.addClass('is-active');

            $('.corporate-slider .corporate-content').removeClass('is-default');
            $('#' + newId).addClass('is-default');

            _this.animateSocialCircle(newId);
        });
    },

    animateSocialCircle: function(idName) {
        $('.social-circle').attr('class', 'social-circle');
        $('.social-circle').addClass('rotate-' + idName);
    }
});

App.CrowdfundingView = Em.View.extend({
    templateName:'how_to_crowdfund'
});

App.HowtoSliderView = Em.View.extend({
    templateName: 'slider',

    didInsertElement: function() {
        var banner = $('.home-carousel .carousel').unslider({
                dots: true,
                fluid: true,
                delay: 800000
            }), _this = this,
            unsliderData = banner.data('unslider');

        $('.carousel-nav-arrow.left').on('click', function() {
            unsliderData.prev();
        });

        $('.carousel-nav-arrow.right').on('click', function() {
            unsliderData.next();
        });
    }

})

App.CivicCrowdfundingView = Em.View.extend({
    templateName:'civic_crowdfunding'
});

