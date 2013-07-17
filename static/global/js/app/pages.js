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

    showTitle: function(){
        console.log(this.get('controller.id'));
        // Don't show title for styled pages
        if (this.get('controller.id') == 'about')return false;
        if (this.get('controller.id') == 'get-involved')return false;
        return true;
    }.property('controller.id'),

    classNames: 'page static-page'.w(),

    setup: function() {
        Ember.run.scheduleOnce('afterRender', this, function() {
            if (!Em.none(this.$())) {
                this.renderSections();
                this.bindEvents();
            }
        });
    }.observes('controller.body'),

    willDestroyElement: function() {
        this.unbindEvents();
    },

    bindEvents: function() {
        var $businessProducts = this.$('#businessProducts');
        $businessProducts.on('mouseenter', '.item', $.proxy(this.popover, this));
        $businessProducts.on('mouseleave', '.item', $.proxy(this.popout, this));

        $(window).on('resize', $.proxy(this.renderSections, this));
    },

    unbindEvents: function() {
        var $businessProducts = this.$('#businessProducts');
        $businessProducts.off('mouseenter', '.item', $.proxy(this.popover, this));
        $businessProducts.off('mouseleave', '.item', $.proxy(this.popout, this));

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

    popover: function(e) {
        var content = $(e.target).data('content');
        this.$('.item-popover').html(content);
    },

    popout: function() {
        this.$('.item-popover').empty();
    }
});

