function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrf_token = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // If url starts with / it's relative and same origin
    if (url.substr(0, 1) == '/') {
        return true;
    }
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/');
    // or any other URL that isn't scheme relative or absolute i.e relative. !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        }
    }
});


Em.TextField.reopen({
    // Add 'step' to attributeBinding
    attributeBindings: ['type', 'value', 'size', 'step']
});

// TODO Rename App to BlueBottle, BB or BBApp.
App = Em.Application.create({
    VERSION: '1.0.0',

    ready: function() {
        //..init code goes here...
    },

    _getTemplate: function(template, callback) {
        var hash = {};
        hash.url = '/en/templates/' + template + '.hbs';
        hash.type = 'GET';
        hash.contentType = 'application/json';
        hash.success = callback;
        hash.error = function(jqXHR, textStatus, errorThrown) {
            throw errorThrown + ' ' + hash.url;
        };
        jQuery.ajax(hash);
    },

    loadTemplate: function(templateFilename) {
        this._getTemplate(templateFilename, function(data) {
            // Iterate through handlebar tags
            $(data).filter('script[type="text/x-handlebars"]').each(function() {
                var templateName = $(this).attr('data-template-name');
                var raw = $(this).html();
                Em.TEMPLATES[templateName] = Em.Handlebars.compile(raw);
            });
        });
    },

    loadTemplates: function(templateFilenames) {
        var app = this;
        templateFilenames.forEach(function (templateFilename) {
            app.loadTemplate(templateFilename);
        });
    }
});


// Load the Handlebar templates.
// TODO: This is race condition that needs to be addressed but should work most of the time.
// TODO We want to actually figure out a way to load the templates on-demand and not do it like this.
App.loadTemplates(['projects', 'wallposts', 'reactions', 'orders', 'vouchers']);


// The Ember Data Adapter and Store configuration.

App.Adapter = DS.DRF2Adapter.extend({
    namespace: "i18n/api",

    plurals: {
        "projects/wallposts/media": "projects/wallposts/media",
        "projects/wallposts/text": "projects/wallposts/text",
        "fund/paymentinfo": "fund/paymentinfo",
        "fund/paymentmethodinfo": "fund/paymentmethodinfo"
    }

});

// Embedded Model Mapping
//
// http://stackoverflow.com/questions/14320925/how-to-make-embedded-hasmany-relationships-work-with-ember-data/14324532#14324532
// The two possible values of embedded are:
//   load: The child records are embedded when loading, but should be saved as standalone records. In order
//         for this to work, the child records must have an ID.
//   always: The child records are embedded when loading, and are saved embedded in the same record. This,
//           of course, affects the dirtiness of the records (if the child record changes, the adapter will
//           mark the parent record as dirty).
App.Adapter.map('App.Project', {
    owner: {embedded: 'load'},
    country: {embedded: 'load'}
});
App.Adapter.map('App.ProjectWallPost', {
    author: {embedded: 'load'},
    photos: {embedded: 'load'},
    reactions: {embedded: 'load'}
});
App.Adapter.map('App.ProjectTextWallPost', {
    author: {embedded: 'load'},
    photos: {embedded: 'load'},
    reactions: {embedded: 'load'}
});
App.Adapter.map('App.ProjectMediaWallPost', {
    author: {embedded: 'load'},
    photos: {embedded: 'load'},
    reactions: {embedded: 'load'}
});
App.Adapter.map('App.WallPostReaction', {
    author: {embedded: 'load'}
});
App.Adapter.map('App.Order', {
    donations: {embedded: 'load'},
    vouchers: {embedded: 'load'}
});
App.Adapter.map('App.CurrentOrder', {
    donations: {embedded: 'load'},
    vouchers: {embedded: 'load'}
});


App.Store = DS.Store.extend({
    revision: 11,
    adapter: 'App.Adapter'
});


/* User / Member authentication. */

// TODO The models are not worked properly yet.
App.Member = DS.Model.extend({
    url: 'members/users',

    username: DS.attr('string'),
    first_name: DS.attr('string'),
    last_name: DS.attr('string'),
    picture: DS.attr('string'),

    full_name: function() {
        return this.get('first_name') + ' ' + this.get('last_name');
    }.property('first_name', 'last_name')
});


App.User = App.Member.extend({
    url: 'members',
    email: DS.attr('string')
});


// Inspiration from:
// http://stackoverflow.com/questions/14388249/accessing-controllers-from-other-controllers
App.CurrentUserController = Em.ObjectController.extend({
    init: function() {
        this._super();
        this.set("model", App.User.find('current'));
    },

    isAuthenticated: function(){
        return (this.get('username')) ? true : false;
    }.property('username')
});


App.ApplicationController = Ember.Controller.extend({
    needs: ['currentUser']
});


/* Routing */

App.SlugRouter = Em.Mixin.create({
    serialize: function(model, params) {
        if (params.length !== 1) { return {}; }

        var name = params[0], object = {};
        object[name] = get(model, 'slug');

        return object;
    }
});


App.Router.map(function() {
    this.route("home", { path: "/" });

    this.resource('projectList', {path: '/projects'}, function() {
        this.route('new');
        this.route('search');
    });

    this.resource('project', {path: '/projects/:project_id'}, function() {
        this.route('edit');
        this.resource('projectWallPost', {path: '/wallposts/:projectwallpost_id'});
    });

    this.resource('currentOrder', {path: '/support'}, function() {
        this.route('donationList', {path: '/donations'});
        this.route('addDonation', {path: '/donations/add/:project_id'});
        this.route('voucherList', {path: '/vouchers'});
        this.route('paymentProfile', {path: '/details'});
        // TODO: Read the manual to see if this is the best way to do it.
        this.resource('currentOrderPayment', {path: '/payment'}, function(){
            this.resource('currentPaymentMethodInfo', {path: 'info'});
        });
    });

    this.resource('finalOrderItemList', {path: '/support/thanks'});

    this.resource('voucherStart', {path: '/vouchers'});
    this.resource('customVoucherRequest', {path: '/vouchers/custom'});
    this.resource('voucherRedeemDone', {path: '/vouchers/redeem/done'});

    this.resource('voucherRedeem', {path: '/vouchers/redeem'}, function() {
        this.route('add', {path: '/add/:slug'});
        this.route('code', {path: '/:code'});
    });
});


App.ProjectListRoute = Ember.Route.extend({
    model: function() {
        return App.Project.find({phase: 'fund'});
    }
});


/**
 * Project Routes
 */

App.ProjectRoute = Ember.Route.extend({
    setupController: function(controller, project) {
        this._super(controller, project);

        // Look if we've got an active voucher
        var voucher = this.controllerFor('voucherRedeem').get('voucher');
        controller.set('currentVoucher', voucher);

        // The RecordArray returned by findQuery can't be manipulated directly so we're temporarily setting it the
        // wallposts property. The controller will convert it to an Ember Array.
        var wallPostListController = this.controllerFor('projectWallPostList');
        wallPostListController.set('wallposts', App.ProjectWallPost.find({project: project.get('id')}));

        // Set the current project on the WallPost new controller.
        this.controllerFor('projectWallPostNew').set('currentProject', project);
    }
});


App.ProjectWallPostRoute = Ember.Route.extend({
    model: function(params) {
        return App.ProjectWallPost.find(params.projectwallpost_id);
    },

    setupController: function(controller, wallpost) {
        controller.set('content', wallpost);
    }
});


/**
 * Current Order Routes
 */

App.CurrentOrderRoute = Ember.Route.extend({
    model: function(params) {
        return App.CurrentOrder.find('current');
    },

    setupController: function(controller, order) {
        this._super(controller, order);
    }
});


// Redirect to the donations list if somebody tries load '/support'.
App.CurrentOrderIndexRoute = Ember.Route.extend({
    redirect: function() {
        this.transitionTo('currentOrder.donationList');
    }
});


App.CurrentOrderDonationListRoute = Ember.Route.extend({
    model: function(params) {
        var order = this.modelFor('currentOrder');
        return order.get('donations');
    },

    setupController: function(controller, donations) {
        this._super(controller, donations);
        this.controllerFor('currentOrder').set('isVoucherOrder', false);
    }
});


// This route is not really an application state we want but it doesn't seem possible to send a parameter (e.g. the
// project) to a route without having a parameter in the URL. This could be a missing feature in Ember or we could be
// missing something. More investigation is needed if we want to get rid of this route.
// Note: This route allows us to publish urls like; '/support/donations/add/<project slug>'
// which will add a donation the project in the current user's cart.
App.CurrentOrderAddDonationRoute = Ember.Route.extend({
    setupController: function (controller, project) {
        var order = this.modelFor('currentOrder');
        if (!order.get('isLoaded')) {
            var route = this;
            order.on("didLoad", function () {
                route.send('addDonation', order, project);
            });
        } else {
            this.send('addDonation', order, project);
        }
    },

    events: {
        addDonation: function (order, project) {
            if (!Em.isNone(project)) {
                var transaction = this.get('store').transaction();
                var donation = transaction.createRecord(App.CurrentOrderDonation);
                transaction.add(donation);
                donation.set('project', project);
                donation.set('order', order);
                transaction.commit();
            }

            // We're transitioning to the donation list route directly after adding the donation so that the url
            // doesn't show '/support/donations/add/slug' after the donation has been added.
            this.transitionTo('currentOrder.donationList');
        }
    }
});


App.CurrentOrderVoucherListRoute = Ember.Route.extend({
    model: function(params) {
        return App.CurrentOrder.find('current').get('vouchers');
    },

    setupController: function(controller, vouchers) {
        this._super(controller, vouchers);
        this.controllerFor('currentOrder').set('isVoucherOrder', true);
    }
});


App.PaymentProfileRoute = Ember.Route.extend({
    model: function(params) {
        return App.PaymentOrderProfile.find('current');
    },

    setupController: function(controller, orderprofile) {
        controller.set('content', orderprofile);
    }
});


/**
 * Vouchers Redeem Routes
 */

App.CustomVoucherRequestRoute = Ember.Route.extend({
    setupController: function(controller, context) {
        // TODO: Find out why init() doesn't run automatically.
        controller.init();
    }
});


App.VoucherRedeemCodeRoute = Ember.Route.extend({
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


App.VoucherRedeemAddRoute = Ember.Route.extend({
    setupController: function(controller, project) {
        var voucher = this.controllerFor('voucherRedeem').get('voucher');
        if (project !== undefined) {
            var transaction = this.get('store').transaction();
            // TODO: Generify and move to DRF2 adapter.
            App.VoucherDonation.reopen({
                url: 'fund/vouchers/' + voucher.get('code') + '/donations'
            });
            var donation = transaction.createRecord(App.VoucherDonation);
            donation.set('project', project);
            // Ember object embedded isn't updated by server response. Manual update for embedded donation here.
            donation.on('didCreate', function(record){
                voucher.get('donations').clear();
                voucher.get('donations').pushObject(record);
            });
            transaction.commit();
        }
    }
});


App.CurrentPaymentMethodInfoRoute = Ember.Route.extend({
    model: function(params) {
        return App.PaymentMethodInfo.find('current');
    },

    setupController: function(controller, paymentmethodinfo) {
        controller.set('content', paymentmethodinfo);
    }
});


App.FinalOrderItemListRoute = Ember.Route.extend({
    model: function(params) {
        return App.LatestDonation.find();
    },

    setupController: function(controller, orderitems) {
        controller.set('content', orderitems);
    }
});


