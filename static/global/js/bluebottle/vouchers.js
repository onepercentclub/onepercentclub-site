/**
 * Router map
 */


// Voucher routes
App.Router.map(function(){

//    Voucher code is disabled for now.
//    this.resource('voucherStart', {path: '/giftcards'});
//    this.resource('customVoucherRequest', {path: '/giftcards/custom'});
//    this.route('customVoucherRequestDone', {path: '/giftcards/custom/done'});
//
//    this.resource('voucherRedeem', {path: '/giftcards/redeem'}, function() {
//        this.route('add', {path: '/add/:project_id'});
//        this.route('code', {path: '/:code'});
//    });
//    this.resource('voucherRedeemDone', {path: '/giftcards/redeem/done'});
});


/* Routes */


/**
 * Vouchers Redeem Routes
 */

App.CustomVoucherRequestRoute = Em.Route.extend({
    setupController: function(controller, context) {
        // TODO: Find out why init() doesn't run automatically.
        controller.init();
    }
});


App.VoucherRedeemCodeRoute = Em.Route.extend({
    model: function(params) {
        var voucher = App.Voucher.find(params['code']);
        // We don't get the code from the server, but we want it to return it to the user here.
        voucher.set('code', params['code']);
        return voucher;
    },

    setupController: function(controller, voucher) {
        this.controllerFor('voucherRedeem').set('voucher', voucher);
    }
});


App.VoucherRedeemAddRoute = Em.Route.extend({

    setupController: function (controller, project) {
        var voucher = this.controllerFor('voucherRedeem').get('voucher');
        if (!voucher.get('isLoaded')) {
            var route = this;
            voucher.one("didLoad", function () {
                route.send('addDonation', voucher, project);
            });
        } else {
            this.send('addDonation', voucher, project);
        }
    },

    actions: {
        addDonation: function (voucher, project) {
            if (!Em.isNone(project)) {
                var store = this.get('store');
                App.VoucherDonation.reopen({
                    url: 'fund/vouchers/' + voucher.get('code') + '/donations'
                });
                var donation = store.createRecord(App.VoucherDonation);
                donation.set('project', project);
                donation.set('voucher', voucher);
                // Ember object embedded isn't updated by server response. Manual update for embedded donation here.
                donation.on('didCreate', function(record) {
                    voucher.get('donations').clear();
                    voucher.get('donations').pushObject(record);
                });
                donation.save();
                $.colorbox.close();
            }
        }
    }
});

App.VoucherRedeemRoute = Em.Route.extend({

    actions: {
        addDonation: function (voucher, project) {
            if (!Em.isNone(project)) {
                var store = this.get('store');
                App.VoucherDonation.reopen({
                    url: 'fund/vouchers/' + voucher.get('code') + '/donations'
                });
                var donation = store.createRecord(App.VoucherDonation);
                donation.set('project', project);
                donation.set('voucher', voucher);
                // Ember object embedded isn't updated by server response. Manual update for embedded donation here.
                donation.on('didCreate', function(record) {
                    voucher.get('donations').clear();
                    voucher.get('donations').pushObject(record);
                });
                donation.save();
                $.colorbox.close();
            }
        }
    }
});


/* Models */

App.CustomVoucherRequest = DS.Model.extend({
    url: 'fund/customvouchers',

    number: DS.attr('number', {defaultValue: 100}),
    type: DS.attr('string', {defaultValue: 'unknown'}),
    contact_name: DS.attr('string', {defaultValue: ''}),
    contact_email: DS.attr('string', {defaultValue: ''}),
    contact_phone: DS.attr('string', {defaultValue: ''}),
    organization: DS.attr('string', {defaultValue: ''}),
    message: DS.attr('string', {defaultValue: ''})
});


App.VoucherDonation = App.Donation.extend({
    url: 'fund/vouchers/:code/donations',
    voucher: DS.belongsTo('App.Voucher')
});


/* Controllers */

App.VoucherRedeemController = Em.ArrayController.extend({
    code: "",

    error: function(){
        if (this.get('voucher.isLoaded')) {
            // we don't get the code from the server, but store it here for future reference.
            this.set('voucher.code', this.get('code'));
            return false;
        }
        if (this.get('voucher')) {
            return true;
        }
        return false;
    }.property('voucher.isSaving', 'voucher.isLoaded'),

    submitVoucherCode: function() {
        var code = this.get('code');
        if (code) {
            var voucher = App.Voucher.find(code);
            this.set('voucher', voucher);

        }
    },

    redeemVoucher: function() {
        var controller = this;
        var voucher = this.get('voucher');
        var transaction = this.get('store').transaction();
        transaction.add(voucher);
        voucher.set('status', 'cashed');
        voucher.on('didUpdate',function(){
            controller.transitionToRoute('voucherRedeemDone');
        });
        transaction.commit();
    },

    // Currently not used. Keep this around for multiple Donations per Voucher.
    deleteVoucherDonation: function(orderItem) {
        var transaction = this.get('store').transaction();
        transaction.add(orderItem);
        orderItem.deleteRecord();
        transaction.commit();
    }
});


App.CustomVoucherRequestController = Em.ObjectController.extend({
    needs: ['currentUser'],

    init: function() {
        this._super();
        this.createCustomVoucherRequest();
    },

    createCustomVoucherRequest: function() {
        var transaction = this.get('store').transaction();
        var voucherRequest =  transaction.createRecord(App.CustomVoucherRequest);
        voucherRequest.set('contact_name', this.get('controllers.currentUser.full_name'));
        voucherRequest.set('contact_email', this.get('controllers.currentUser.email'));
        var view = this;
        voucherRequest.on('didCreate',function(){
            view.transitionToRoute('customVoucherRequestDone');
        });
        this.set('content', voucherRequest);
        this.set('transaction', transaction);

    },

    sendRequest: function() {
        var transaction = this.get('transaction');
        var voucherRequest = this.get('content');
        transaction.commit();
    }
});


App.VoucherPickProjectController = Em.ArrayController.extend({
    // Because this hasn't got a Route we get the list over here
    init: function(){
        this._super();
        this.set('projects', App.Project.find({phase: 'campaign'}));
    }
});


/* Views */

App.VoucherStartView = Em.View.extend({
    tagName: 'div',
    templateName: 'voucher_start'
});


App.VoucherRedeemView = Em.View.extend({
    tagName: 'div',
    templateName: 'voucher_redeem'
});


App.VoucherRedeemDoneView = Em.View.extend({
    tagName: 'div',
    templateName: 'voucher_redeem_done'
});


App.CustomVoucherRequestView = Em.View.extend({
    tagName: 'form',
    templateName: 'custom_voucher_request'
});


App.CustomVoucherRequestDoneView = Em.View.extend({
    templateName: 'custom_voucher_request_done'
});


App.VoucherDonationView = Em.View.extend({
    templateName: 'voucher_donation',
    tagName: 'li',
    classNames: 'donation-project control-group',

    neededAfterDonation: function () {
        return '';
    }.property('project', 'voucher'),

    'delete': function(item){
        var controller = this.get('controller');
        this.$().slideUp(500, function() {
            controller.deleteOrderItem(item)
        });
    }
});

App.VoucherPickProjectView = Em.View.extend({
    templateName: 'voucher_pick_project'
});

