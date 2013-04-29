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
    // Update attributeBinding with 'step' and 'multiple'
    attributeBindings: ['type', 'value', 'size', 'step', 'multiple']
});


// TODO Rename App to BlueBottle, BB or BBApp.
App = Em.Application.create({
    VERSION: '1.0.0',

    // TODO: Remove this in production builds.
    LOG_TRANSITIONS: true,

    // TODO: Make sure to avoid race conditions. See if we can dynamically load this as needed.
    templates: ['profiles', 'projects', 'wallposts', 'reactions', 'orders', 'vouchers'],

    // We store language & locale here because they need to be available before loading templates.
    language: 'en',
    locale: 'en-GB',
    interfaceLanguages: [
        Em.Object.create({name:'English', code: 'en'}),
        Em.Object.create({name:'Nederlands', code: 'nl'})
    ],

    ready: function() {
        // Read language string from url.
        var language = window.location.pathname.split('/')[1];
        // We don't have to check if it's one of the languages available. Django will have thrown an error before this.
        this.set('language', language);

        // Now that we know the language we can load the hb templates.
        this.loadTemplates(this.templates);

        // Read locale from browser with fallback to default.
        var locale = navigator.language || navigator.userLanguage || this.get('locale');
        if (locale.substr(0, 2) != language) {
            // Some overrides to have a sound expereince, at least for dutch speaking and dutch based users.

            if (language == 'nl') {
                // For dutch language always overwrite locale. Always use dutch locale.
                locale = 'nl';
            }
            if (language == 'en' && locale.substr(0, 2) == 'nl') {
                // For dutch browser viewing english site overwrite locale.
                // We don't want to have dutch fuzzy dates.
                // If fuzzy dates are translated in other languages we should decide if we want to show those.
                locale = 'en';
            }
        }
        this.setLocale(locale);
    },

    setLocale: function(locale) {
        if (!locale) {
            locale = this.get('locale');
        }

        if (locale != 'en-US') {
            // Try to load locale specifications.
            $.getScript('/static/assets/js/libs/globalize-cultures/globalize.culture.' + locale + '.js')
                .fail(function(){
                    console.log("No globalize culture file for : "+ locale);
                    // Specified locale file not available. Use default locale.
                    locale = App.get('locale');
                    Globalize.culture(locale);
                    App.set('locale', locale);
                })
                .success(function(){
                    // Specs loaded. Enable locale.
                    Globalize.culture(locale);
                    App.set('locale', locale);
                });

        } else {
            Globalize.culture(locale);
            App.set('locale', locale);
        }
    },

    _getTemplate: function(template, callback) {
        var language = this.get('language');
        var hash = {};
        hash.url = '/' + language + '/templates/' + template + '.hbs';
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


App.Adapter.map('App.Payment', {
  availablePaymentMethods: { readOnly: true }
});


App.ApplicationController = Ember.Controller.extend({
    needs: ['currentUser']
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
App.Adapter.map('App.ProjectSupporter', {
    project: {embedded: 'load'},
    member: {embedded: 'load'}
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
        this.route('voucherList', {path: '/giftcards'});

        this.resource('paymentProfile', {path: '/details'});
        this.resource('payment', {path: '/payment'});
    });

    this.resource('OrderThanks', {path: '/support/thanks/:order_id'});

    this.resource('voucherStart', {path: '/giftcards'});
    this.resource('customVoucherRequest', {path: '/giftcards/custom'});
    this.route('customVoucherRequestDone', {path: '/giftcards/custom/done'});
    this.resource('voucherRedeemDone', {path: '/giftcards/redeem/done'});

    this.resource('voucherRedeem', {path: '/giftcards/redeem'}, function() {
        this.route('add', {path: '/add/:project_id'});
        this.route('code', {path: '/:code'});
    });

});


App.ApplicationRoute = Ember.Route.extend({

    events: {
        selectLanguage: function(language) {
            if (language == App.get('language')) {
                // Language already set. Don't do anything;
                return true;
            }
            var languages = App.get('interfaceLanguages');
            for (i in languages) {
                // Check if the selected language is available.
                if (languages[i].code == language) {
                    document.location = '/' + language + document.location.hash;
                    return true;
                }
            }
            language = 'en';
            document.location = '/' + language + document.location.hash;
            return true;
        },
        openInBox: function(name, context){
            // Get the controller or create one
            var controller = this.controllerFor(name);
            controller.set('model', context);

            // Get the view. This should be defined.
            var view = App[name.classify() + 'View'].create();
            view.set('controller', controller);

            //var html = view.render();
            // console.log(html);
            // $.colorbox({html: ' ', height: 600, width: 800});
            // view.appendTo('#cboxLoadedContent');
            Bootstrap.ModalPane.popup({
                html: view
            });

        }
    }
});


/**
 * Project Routes
 */

App.ProjectListRoute = Ember.Route.extend({
    model: function() {
        return App.Project.find({phase: 'fund'});
    }
});


App.ProjectRoute = Ember.Route.extend({
    setupController: function(controller, project) {
        this._super(controller, project);

        // The RecordArray returned by findQuery can't be manipulated directly so we're temporarily setting it the
        // wallposts property. The controller will convert it to an Ember Array.
        var wallPostListController = this.controllerFor('projectWallPostList');
        wallPostListController.set('wallposts', App.ProjectWallPost.find({project: project.get('id')}));
        wallPostListController.set('page', 1);
        wallPostListController.set('canLoadMore', true);

        // Set the current project on the WallPost new controller.
        this.controllerFor('projectWallPostNew').set('currentProject', project);

        // Set the controller to show Project Supporters
        var projectSupporterListController = this.controllerFor('projectSupporterList');
        projectSupporterListController.set('supporters', App.ProjectSupporter.find({project: project.get('id')}));
        projectSupporterListController.set('page', 1);
        projectSupporterListController.set('canLoadMore', true);
    },

    events: {
        showMoreWallPosts: function(){
            var controller = this.controllerFor('projectWallPostList');
            var page = controller.incrementProperty('page');
            var project = this.controllerFor('project');
            var wps = App.ProjectWallPost.find({project: project.get('id'), page: page});
            controller.set('canLoadMore', false);
            wps.addObserver('isLoaded', function(){
                wps.forEach(function(record){
                    if (record.get('isLoaded')) {
                        controller.pushObject(record);
                    }
                });
                controller.set('canLoadMore', true);
            });
        }
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
            this.replaceWith('currentOrder.donationList');
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


/**
 * Payment for Current Order Routes
 */

App.PaymentProfileRoute = Ember.Route.extend({
    model: function(params) {
        return App.PaymentProfile.find('current');
    },

    setupController: function(controller, paymentProfile) {
        this._super(controller, paymentProfile);
    }
});


App.PaymentRoute = Ember.Route.extend({
    model: function(params) {
        return App.Payment.find('current');
    },

    setupController: function(controller, payment) {
        this._super(controller, payment);
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

    setupController: function (controller, project) {
        var voucher = this.controllerFor('voucherRedeem').get('voucher');
        if (!voucher.get('isLoaded')) {
            var route = this;
            voucher.on("didLoad", function () {
                route.send('addDonation', voucher, project);
            });
        } else {
            this.send('addDonation', voucher, project);
        }
    },

    events: {
        addDonation: function (voucher, project) {
            if (!Em.isNone(project)) {
                var transaction = this.get('store').transaction();
                App.VoucherDonation.reopen({
                    url: 'fund/vouchers/' + voucher.get('code') + '/donations'
                });
                var donation = transaction.createRecord(App.VoucherDonation);
                transaction.add(donation);
                donation.set('project', project);
                donation.set('voucher', voucher);
                // Ember object embedded isn't updated by server response. Manual update for embedded donation here.
                donation.on('didCreate', function(record){
                    voucher.get('donations').clear();
                    voucher.get('donations').pushObject(record);
                });
                transaction.commit();
                $.colorbox.close();
            }
        }
    }
});


/* Views */

App.LanguageView = Ember.View.extend({
    templateName: 'language'
});


App.LanguageSwitchView = Ember.CollectionView.extend({
    tagName: 'ul',
    classNames: ['nav-language'],
    content: App.interfaceLanguages,
    itemViewClass: App.LanguageView
});


App.LoginView = Em.View.extend({
    templateName: "login"
});

