/* Models */

App.Page = DS.Model.extend({
    url: 'pages',
    title: DS.attr('string'),
    body: DS.attr('string')
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
    classNames: 'page static-page'.w(),

    setup: function() {
        Ember.run.scheduleOnce('afterRender', this, function() {
            this.manageSections();
            $(window).on('resize', $.proxy(this.manageSections, this));
        });
    }.observes('controller.body'),

    willDestroyElement: function() {
        $(window).off('resize', $.proxy(this.manageSections, this));
    },

    manageSections: function(e) {
        if (this.$('.static')) {
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
        }
    }
});
