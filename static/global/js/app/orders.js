/*
 Models
 */

App.Order = DS.Model.extend({
    url: 'fund/orders',
    amount: DS.attr('number'),
    status: DS.attr('string'),
    recurring: DS.attr('string')
});


App.PaymentOrderProfile = DS.Model.extend({
    url: 'fund/paymentorderprofiles',
    firstName: DS.attr('string'),
    lastName: DS.attr('string'),
    email: DS.attr('string'),
    street: DS.attr('string'),
    city: DS.attr('string'),
    country: DS.attr('string'),
    postalCode: DS.attr('string')
});

App.OrderItem = DS.Model.extend({
    url: 'fund/orders/:order_id/items',

    // Model fields
    // FIXME Make the drf2 serializer use the id (or slug) to serialize DS.belongsTo.
    //       This will enable us to remove the project_slug field.
    project: DS.belongsTo('App.Project'),
    project_slug: DS.attr('string'),
    amount: DS.attr('number'),
    status: DS.attr('string'),
    type: DS.attr('string')
});


App.CurrentOrderItem = DS.Model.extend({
    url: 'fund/orders/current/items'
});


App.LatestDonation = App.OrderItem.extend({
    url: 'fund/orders/latest/donations'
});

App.CurrentDonation = App.OrderItem.extend({
    url: 'fund/orders/current/donations'
});



App.CurrentVoucher = App.OrderItem.extend({
    url: 'fund/orders/current/vouchers'
});


App.PaymentInfo = DS.Model.extend({
    url: 'fund/paymentinfo',
    payment_method: DS.attr('number'),
    amount: DS.attr('number'),
    firstName: DS.attr('string'),
    lastName: DS.attr('string'),
    address: DS.attr('string'),
    city: DS.attr('string'),
    country: DS.attr('string'),
    zipCode: DS.attr('string'),
    payment_url: DS.attr('string')
});


App.Payment = DS.Model.extend({
    url: 'fund/payments',
    payment_method: DS.attr('string'),
    amount: DS.attr('number'),
    status: DS.attr('string')
});


/*
 Controllers
 */


App.CurrentOrderItemListController = Em.ArrayController.extend({

    updateOrderItem: function(orderItem, newAmount) {
        var transaction = App.store.transaction();
        transaction.add(orderItem);
        orderItem.set('amount', newAmount);
        transaction.commit();
    },

    deleteOrderItem: function(orderItem) {
        var transaction = App.store.transaction();
        transaction.add(orderItem);
        orderItem.deleteRecord();
        transaction.commit();
    }
});



App.PaymentOrderProfileController = Em.ObjectController.extend({

    initTransaction: function(){
        var transaction = App.store.transaction();
        this.set('transaction', transaction);
        transaction.add(this.get('content'));
    }.observes('content'),

    updateProfile: function(){
        var profile = this.get('content');
        var controller = this;
        // We should at least have an email address
        if (!profile.get('isDirty') && profile.get('email')) {
            // No changes. No need to commit.
            controller.transitionTo('orderPayment');
        }
        this.get('transaction').commit();
        profile.on('didUpdate', function(record) {
            controller.transitionTo('orderPayment');
        });
        // TODO: Validate data and return errors here
        profile.on('becameInvalid', function(record) {
            controller.get('content').set('errors', record.get('errors'));

        });
    }
});


App.CurrentOrderController = Em.ObjectController.extend({

    initTransaction: function(){
        var order = this.get('content');
        var transaction = App.get('store').transaction();
        this.set('transaction', transaction);
        transaction.add(order);
    }.observes('content'),

    updateOrder: function(){
        if (this.get('content.isDirty')) {
            var controller = this;
            var order = this.get('content');
            this.get('transaction').commit();
            order.on('didUpdate', function(){
                // Init a new private transaction.
                controller.initTransaction();
            });

        }
    }.observes('content.isDirty')
});


App.OrderPaymentController = Em.ObjectController.extend({

    initTransaction: function(){
        var transaction = App.store.transaction();
        this.set('transaction', transaction);
        transaction.add(this.get('content'));
    }.observes('content'),

    updateOrderPayment: function(){
        if (this.get('content.isDirty')) {
            var controller = this;
            var orderPayment = this.get('content');
            this.get('transaction').commit();
            orderPayment.on('didUpdate', function(){
                controller.transitionTo('paymentInfo')
                controller.initTransaction();
            });
        }
    }.observes('content.isDirty')
});

/*
 Views
 */

App.CurrentOrderView = Em.View.extend({
    templateName: 'current_order'
});


App.PaymentOrderProfileView = Em.View.extend({
    templateName: 'payment_order_profile',
    tagName: 'form',
    submit: function(e){
        e.preventDefault();
        this.controller.updateProfile();
    }
});


App.CurrentOrderItemListView = Em.View.extend({
    templateName: 'currentorderitem_form',
    tagName: 'form'
});


App.FinalOrderItemListView = Em.View.extend({
    templateName: 'final_order_item_list',
    tagName: 'div'
});


App.CurrentOrderItemView = Em.View.extend({
    templateName: 'currentorderitem',
    tagName: 'li',
    classNames: 'donation-project',

    neededAfterDonation: function() {
        return this.get('content.project.money_needed_natural') - this.get('content.amount');
    }.property('content.amount', 'content.project.money_needed_natural'),

    change: function(e){
        this.get('controller').updateOrderItem(this.get('content'), Em.get(e, 'target.value'));
    },

    delete: function(item){
        var controller = this.get('controller');
        this.$().slideUp(500, function(){controller.deleteOrderItem(item)});
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


App.OrderPaymentView = Em.View.extend({
    tagName: 'form',
    templateName: 'order_payment',

    // TODO: Find out why this.get('content') isn't available...
    highlightSelected: function(){
        // On first load highlight the selected option
        console.log('hup: ' + this.get('content.payment_method'));
        this.$('input').parents('label').removeClass('selected');
        this.$('input[value='+this.get('content.payment_method')+']').parents('label').addClass('selected');
    }.observes('content.payment_method')


});


App.PaymentInfoView = Em.View.extend({
    tagName: 'form',
    templateName: 'payment_info'
});
