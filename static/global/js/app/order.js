/*
 Models
 */

App.OrderProfile = DS.Model.extend({
    url: 'fund/orders/profiles',
    firstName: DS.attr('string'),
    lastName: DS.attr('string'),
    email: DS.attr('string'),
    address: DS.attr('string'),
    city: DS.attr('string'),
    country: DS.attr('string'),
    zipCode: DS.attr('string')
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
    payment_method: DS.attr('number'),
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


App.OrderProfileController = Em.ObjectController.extend({
    transaction: null,

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
            //profile.set('errors', record.get('errors'));
        });
    }
});

/*
 Views
 */

App.CurrentOrderView = Em.View.extend({
    templateName: 'current_order'
});


App.OrderProfileView = Em.View.extend({
    templateName: 'order_profile_form',
    tagName: 'form',
    submit: function(){
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
    neededAfterDonation: function(){
        return this.get('content.project.money_needed_natural') - this.get('content.amount');
    }.property('content.amount', 'content.project.money_needed_natural'),

    change: function(e){
        this.get('controller').updateOrderItem(this.get('content'), Em.get(e, 'target.value'));
    }
});


App.Payment = DS.Model.extend({
    url: 'fund/payments',
    payment_method: DS.attr('number'),
    amount: DS.attr('number'),
    status: DS.attr('string')
});


App.OrderPaymentView = Em.View.extend({
    tagName: 'form',
    templateName: 'order_payment'
});


App.PaymentInfoView = Em.View.extend({
    tagName: 'form',
    templateName: 'payment_info'
});
