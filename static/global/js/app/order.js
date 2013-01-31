/*
 Models
 */

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


App.CurrentDonation = App.OrderItem.extend({
    url: 'fund/orders/current/donations'
});


App.CurrentVoucher = App.OrderItem.extend({
    url: 'fund/orders/current/vouchers'
});


/*
 Controllers
 */

App.CurrentOrderItemListController = Em.ArrayController.extend({

    init: function() {
        this._super();
        console.log(this.toString() + ".init");
    },

    deleteOrderItem: function(donation) {
        var transaction = App.store.transaction();
        transaction.add(donation);
        donation.deleteRecord();
        transaction.commit();
    }

});


App.CurrentOrderController = Em.ObjectController.extend({

    init: function() {
        this._super();
        console.log(this.toString() + ".init");
    }
});


/*
 Views
 */

App.CurrentOrderView = Em.View.extend({
    templateName: 'currentorder',

    init: function() {
        this._super();
        console.log(this.toString() + ".init");
    }

});


App.CurrentOrderItemListView = Em.View.extend({
    templateName: 'currentorderitem_form',
    tagName: 'form',

    init: function() {
        this._super();
        console.log(this.toString() + ".init");
    }

});


App.Payment = DS.Model.extend({
    url: 'fund/payments',
    payment_method: DS.attr('number'),
    amount: DS.attr('number'),
    status: DS.attr('string')
});


App.OrderPaymentController = Em.ObjectController.extend({

});


App.OrderPaymentView = Em.View.extend({
    tagName: 'form',
    templateName: 'order_payment'
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
    zip: DS.attr('string'),
    payment_url: DS.attr('string'),
});


App.PaymentInfoController = Em.ObjectController.extend({

});


App.PaymentInfoView = Em.View.extend({
    tagName: 'form',
    templateName: 'payment_info'
});
