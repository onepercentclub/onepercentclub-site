/* Models */


App.Page = DS.Model.extend({
    url: 'pages',
    title: DS.attr('string'),
    body: DS.attr('string')
});


App.ContactMessage = DS.Model.extend({
    url: 'pages/contact',

    name: DS.attr('string'),
    email: DS.attr('string'),
    message: DS.attr('string'),

    isComplete: function(){
        if (this.get('name') && this.get('email') && this.get('message')){
            return true;
        }
        return false;
    }.property('name', 'email', 'message'),

    isSent: function(){
        if (this.get('id')){
            return true;
        }
        return false;
    }.property('id')
});


App.PartnerOrganization = DS.Model.extend({
    url: 'partners',
    name: DS.attr('string'),
    projects: DS.hasMany('App.ProjectPreview'),
    description: DS.attr('string'),
    image: DS.attr('image')
});

/* Controllers */

App.ContactMessageController = Em.ObjectController.extend({
    needs: ['currentUser'],

    startEditing: function() {
        var record = this.get('model');
        if (record.transaction.isDefault == true) {
            this.transaction = this.get('store').transaction();
            this.transaction.add(record);
        }
    },

    updateRecordOnServer: function(){
        var controller = this;
        var model = this.get('model');
        model.one('becameInvalid', function(record){
            model.set('errors', record.get('errors'));
        });
        model.transaction.commit();
    },

    stopEditing: function() {
    }
});


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
        var menuHeight   = this.$('.static-page-nav').height();

        this.$('.section').css('height', windowHeight + 'px');
        this.$('.static-page-section-content').each(function() {
            var $this = $(this);
            var sectionContentHeight = $this.height();

            $this.css({
                'padding-top': (((windowHeight - sectionContentHeight) / 2) - menuHeight) + 'px'
            });
        });
    },

    didInsertElement: function(e){
		this.$().find('#bannerCarousel').unslider({
            dots: true,
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
                                {top: '92px', left: '78px', rotate: -5},
                                {top: '94px', left: '96px', rotate: 12},
                                {top: '82px', left: '88px', rotate: -5},
                                {top: '82px', left: '63px', rotate: -10},
                                {top: '92px', left: '63px', rotate: 23},
                                {top: '64px', left: '87px', rotate: 0},
                                {top: '87px', left: '78px', rotate: -11},
                                {top: '87px', left: '78px', rotate: -9},
                                {top: '92px', left: '87px', rotate: 0},
                                {top: '86px', left: '89px', rotate: 3},
                                {top: '91px', left: '76px', rotate: -3},
                                {top: '101px', left: '79px', rotate: 7},
                                {top: '10000px', left: '-1000px', rotate: 7},
                            ]

                            var t = 0;
                            var m = [];
                            $('div.image').each(function(crew){
                                m[t] = moust.clone();
                                $(this).append(m[t]);
                                if (loc[t] != undefined) {
                                    var degree = loc[t].rotate;
                                    console.log(degree);
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
