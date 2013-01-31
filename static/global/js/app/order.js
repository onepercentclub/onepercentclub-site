

App.OrderItem = DS.Model.extend({
    url: 'fund/orders/:order_id/items',

    // Model fields
    // FIXME Make the drf2 serializer use the id (or slug) to serialize DS.belongsTo. This will enable us to remove
    //       the project_slug field.
    project: DS.belongsTo('App.Project'),
    project_slug: DS.attr('string'),
    amount: DS.attr('number'),
    status: DS.attr('string'),
    type: DS.attr('string')
});


App.CartOrderItem = DS.Model.extend({
    url: 'fund/orders/cart/items',
});


App.CartDonation = App.OrderItem.extend({
    url: 'fund/orders/cart/donations'
});

App.CartVoucher = App.OrderItem.extend({
    url: 'fund/orders/cart/vouchers'
});

App.CartOrderItemListController = Em.ArrayController.extend({

    init: function() {
        this._super();
        console.log(this.toString() + ".init");
    }
});

App.CartOrderController = Em.ObjectController.extend({

    init: function() {
        this._super();
        console.log(this.toString() + ".init");
    }
});


App.CartOrderView = Em.View.extend({
    templateName: 'cartorder',
    init: function() {
        this._super();
        console.log(this.toString() + ".init");
    }

});

App.CartOrderItemListView = Em.View.extend({
    templateName: 'cartorderitem_form',
    tagName: 'form',
    init: function() {
        this._super();
        console.log(this.toString() + ".init");
    },

    submit: function(e) {
        e.preventDefault()
        console.log("cart orderitem list - submit")

    }

});