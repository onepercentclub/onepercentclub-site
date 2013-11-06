
/*
 Views
 */

App.PaymentProfileView = Em.View.extend({
    submit: function(e) {
        e.preventDefault();
        this.get('controller').updateProfile();
    }
});

App.PaymentSignupView = Em.View.extend({
    submit: function(e) {
        e.preventDefault();
        this.get('controller').createUser();
    }
});


App.CurrentOrderDonationListView = Em.View.extend({
    templateName: 'current_order_donation_list',

    submit: function(e) {
        e.preventDefault();
    },

    change: function(e) {
        // The "single" / "monthly" change (strings) and the recurringTotal change (number) are sent here and
        // we only want to deal with the recurringTotal change.
        var value = parseInt(Em.get(e, 'target.value'));
        if (Em.typeOf(value) === 'number' && !isNaN(value)) {
            this.get('controller').set('recurringTotal', value);
        }
    }
});


App.CurrentOrderVoucherListView = Em.View.extend({
    templateName: 'current_order_voucher_list',
    classNames: ['content']
});


App.CurrentOrderDonationView = Em.View.extend({
    tagName: 'li',
    classNames: 'project-list-item',

    change: function(e) {
        this.get('controller').updateDonation(Em.get(e, 'target.value'));
    },
    actions: {
        deleteDonation: function(item) {
            var controller = this.get('controller');
            this.$().slideUp(500, function() {
                controller.deleteDonation();
            });
        }
    }
});


App.CurrentRecurringDonationView = App.CurrentOrderDonationView.extend({
    templateName: 'currentOrderDonation',

    'delete': function(item) {
        var controller = this.get('controller');
        this.$().slideUp(500, function() {
            controller.deleteDonation();
        });
    }
});


App.CurrentOrderVoucherView = Em.View.extend({
    templateName: 'current_order_voucher',
    tagName: 'li',
    classNames: ['voucher-item'],

    'delete': function() {
        var controller = this.get('controller');
        this.$().slideUp(500, function() {
            controller.deleteVoucher()
        });
    }
});


App.CurrentOrderVoucherNewView = Em.View.extend({
    templateName: 'current_order_voucher_new',
    tagName: 'form',
    classNames: ['labeled'],

    submit: function(e) {
        e.preventDefault();
    }
});


App.OrderNavView = Ember.View.extend({
    tagName: 'li',

    didInsertElement: function () {
        this._super();
        if (this.get('childViews.firstObject.active')) {
            this.setOrderProgress();
        }
    },

    childBecameActive: function(sender, key) {
        if (this.get(key) && this.state == "inDOM") {
            this.setOrderProgress()
        }
    }.observes('childViews.firstObject.active'),

    setOrderProgress: function() {
        var highlightClassName = 'is-selected';
        this.$().prevAll().addClass(highlightClassName);
        this.$().nextAll().removeClass(highlightClassName);
        this.$().addClass(highlightClassName);
    }
});


App.RecurringDirectDebitPaymentView = Em.View.extend({
    submit: function(e) {
        e.preventDefault();
        this.get('controller').setRecurringOrder();
    }
});


App.PaymentSelectView = Em.View.extend({
    change: function () {
        $('.radio').removeClass('selected');
        $('.radio:has(input:checked)').addClass('selected');
    }
});


App.TickerView = Em.View.extend({
    // Remove header/footer for this view.
    didInsertElement: function () {
        this._super();
        $('body').css('overflow', 'hidden');
        $('#navigation').remove();
        $('#footer').remove();
    }
});

App.OrderThanksView = Em.View.extend({
    
});