
/*
   Mixin to enable scrolling from one anchor point to another
   within a same page.

   Mix the mixin into View classes like:
   e.g. App.YourView = Ember.View.extend(App.GoTo, {});

   And, In your template,

   <a class="goto" data-target="#Destination">Source</a>

   Or,

   <a {{action 'goTo' '#Destination' target="view" bubbles=false}}>Source</a>
 */
App.GoTo = Ember.Mixin.create({
    click: function(e) {
        var $target = $(e.target);

        if ($target.hasClass('goto')) {
            this.goTo($target.data('target'));
            e.preventDefault();
        }
    },

    goTo: function(target) {
        $('html, body').stop().animate({
            scrollTop: $(target).offset().top
        }, 500);
    }
});


App.PageView = Ember.View.extend(App.GoTo, {
    templateName: 'page',

    showTitle: function(){
        // Don't show title for styled pages
        if (this.get('controller.id') == 'about')return false;
        if (this.get('controller.id') == 'get-involved')return false;
        if (this.get('controller.id') == 'business')return false;
        if (this.get('controller.id') == 'fmo')return false;
        return true;
    }.property('controller.id'),

    classNames: 'page static-page'.w(),

    setup: function() {
        Ember.run.scheduleOnce('afterRender', this, function() {
            if (!Em.isNone(this.$())) {
                this.renderSections();
                this.bindEvents();
            }
        });
    }.observes('controller.body'),

    willDestroyElement: function() {
        this.unbindEvents();
    },

    bindEvents: function() {
        $(window).on('resize', $.proxy(this.renderSections, this));
    },

    unbindEvents: function() {
        $(window).off('resize', $.proxy(this.renderSections, this));
    },

    renderSections: function(e) {
        var windowHeight = $(window).height();
        this.$('.static-onepage-section').css('height', windowHeight + 'px');
        this.$('.static-onepage-content').each(function() {
            // Reset first to get correct height
            $(this).css({
                'position' : 'relative',
                'height' : 'auto'
            });
            $(this).css({
                'height' : $(this).height() + 'px',
                'position' : 'absolute'
            });
        });
    },

    didInsertElement: function(e){
		this.$().find('.carousel').unslider({
            dots: true,
            fluid: true,
            delay: 10000
        });
        if (this.get('controller.id') == 'meet-team') {
            var typeKeys = [72, 69, 76, 76, 79],
                something_index = 0,
                handler = function (e) {
                    if (e.keyCode === typeKeys[something_index++]) {
                        if (something_index === typeKeys.length) {
                            $(document).unbind("keydown", handler);
                            var snd = new Audio('/static/assets/media/hello.mp3');
                            var moust = $('<span style="transform: rotate(5deg);position:absolute;top:-700px;left:40px;width:50px;height:17px;background:url(/static/assets/images/sprites/lionel.png)"><span>')
                            $('div.image').css('position', 'relative');

                            var loc = [
                                {top: '124px', left: '113px', rotate: -5}, // AC
                                {top: '126px', left: '134px', rotate: 12}, // BL
                                {top: '114px', left: '126px', rotate: -5}, // MP
                                {top: '114px', left: '92px', rotate: -10}, //NJ
                                {top: '126px', left: '94px', rotate: 23}, //NE
                                {top: '89px', left: '124px', rotate: 0}, //LG
                                {top: '114px', left: '113px', rotate: -11}, //NT
                                {top: '117px', left: '112px', rotate: -9}, //LM
                                {top: '124px', left: '123px', rotate: 0}, // MG
                                {top: '118px', left: '126px', rotate: 3}, // MH
                                {top: '123px', left: '109px', rotate: -3}, // SS
                                {top: '1000px', left: '-1000px', rotate: 7}
                            ]

                            var t = 0;
                            var m = [];
                            $('div.image').each(function(crew){
                                m[t] = moust.clone();
                                $(this).append(m[t]);
                                if (loc[t] != undefined) {
                                    var degree = loc[t].rotate;
                                    m[t].fadeOut(0);
                                    m[t].fadeIn(1000);
                                    m[t].css({
                                                '-webkit-transform': 'rotate(' + degree + 'deg)',
                                                '-moz-transform': 'rotate(' + degree + 'deg)',
                                                '-ms-transform': 'rotate(' + degree + 'deg)',
                                                '-o-transform': 'rotate(' + degree + 'deg)',
                                                'transform': 'rotate(' + degree + 'deg)',
                                                'zoom': 1
                                    }, 5000);
                                    m[t].animate(loc[t], 10000);
                                }
                                t++;
                            });
                            snd.play()
                        }
                    } else {
                        something_index = 0;
                    }
                };
            $(document).bind("keydown", handler);
        }
    }
});
