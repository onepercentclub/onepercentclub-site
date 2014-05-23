/**
 * Router Map
 */


App.Router.map(function() {
    this.resource('voucher', {path: '/giftcards'}, function() {
        this.resource('voucherRedeem', {path: '/redeem/:code'});
    });
});

/**
 * Current Order Routes
 */

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

// Redirect to the donations list if somebody tries load '/support'.
App.VoucherRedeemRoute = Em.Route.extend({

    model: function(params){
        return App.Voucher.find(params.code);
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
