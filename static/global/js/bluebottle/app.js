// TODO Rename App to BlueBottle, BB or BBApp.
App = Em.Application.create({
    VERSION: '1.0.0',

    // TODO: Remove this in production builds.
    LOG_TRANSITIONS: true,


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
        App.CurrentUser.find('current').then(function(user){
            var primaryLanguage = user.get('primary_language');
            if (primaryLanguage && primaryLanguage != language) {
                document.location = '/' + primaryLanguage + document.location.hash;
            }
        });
        // We don't have to check if it's one of the languages available. Django will have thrown an error before this.
        this.set('language', language);

        // Now that we know the language we can load the handlebars templates.
        //this.loadTemplates(this.templates);

        // Read locale from browser with fallback to default.
        var locale = navigator.language || navigator.userLanguage || this.get('locale');
        if (locale.substr(0, 2) != language) {
            // Some overrides to have a sound experience, at least for dutch speaking and dutch based users.

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

        App.Page.reopen({
            url: 'pages/' + language + '/pages'
        });
        this.initSelectViews();
        this.setLocale(locale);
        this.initSelectViews();
    },

    initSelectViews: function() {
        // Pre-load these lists so we avoid race conditions when displaying forms
        App.Theme.find().then(function(list) {
            App.ThemeSelectView.reopen({
                content: list
            });
        });

        App.Skill.find().then(function(list) {
            App.SkillSelectView.reopen({
                content: list
            });
        });

        App.Country.find().then(function(list) {
            App.CountrySelectView.reopen({
                content: list
            });
            App.CountryCodeSelectView.reopen({
                content: list
            });
        });
        // Get a filtered list of countries that can apply for a project ('oda' countries).
        var filteredList = App.Country.filter(function(item) {return item.get('oda')});

        App.ProjectCountrySelectView.reopen({
            content: filteredList
        });
    },

    setLocale: function(locale) {
        if (!locale) {
            locale = this.get('locale');
        }

        if (locale != 'en-US') {
            // Try to load locale specifications.
            $.getScript('/static/assets/js/vendor/globalize-cultures/globalize.culture.' + locale + '.js')
                .fail(function() {
                    if (window.console && !Ember.testing) {
                        console.log("No globalize culture file for : "+ locale);
                    }
                    // Specified locale file not available. Use default locale.
                    locale = App.get('locale');
                    Globalize.culture(locale);
                    App.set('locale', locale);
                })
                .success(function() {
                    // Specs loaded. Enable locale.
                    Globalize.culture(locale);
                    App.set('locale', locale);
                });
            $.getScript('/static/assets/js/vendor/jquery-ui/i18n/jquery.ui.datepicker-' + locale.substr(0, 2) + '.js')
                .fail(function() {
                    if (window.console && !Ember.testing) {
                        console.log("No jquery.ui.datepicker file for : "+ locale);
                    }
                    // Specified locale file not available. Use default locale.
                    locale = App.get('locale');
                    Globalize.culture(locale);
                    App.set('locale', locale);
                })
                .success(function() {
                    // Specs loaded. Enable locale.
                    App.set('locale', locale);
                });
        } else {
            Globalize.culture(locale);
            App.set('locale', locale);
        }
    }
});


// Mixin to scroll view top top of the screen
App.ScrollInView = Em.Mixin.create({
    didInsertElement: function(a, b){
        var offset = this.$().offset().top - 120;
        var windowOffset = $(window).scrollTop();
        // Only scroll if the focus is more then 50px off.
        if (Math.abs(windowOffset - offset) > 50) {
            $("html, body").animate({ scrollTop: offset }, 600);
        }
    }
});

App.ScrollToTop = Em.Mixin.create({
    afterModel: function(){
        this._super();
        $("html, body").animate({ scrollTop: 0 }, 600);
    }
});


/**
 * The Ember Data Adapter and Store configuration.
 */
App.Adapter = DS.DRF2Adapter.extend({
    namespace: "api",

    plurals: {
        "projects/manage": "projects/manage",
        "projects/pitches/manage": "projects/pitches/manage",
        "projects/plans/manage": "projects/plans/manage",
        "projects/campaigns/manage": "projects/campaigns/manage",
        "projects/wallposts/media": "projects/wallposts/media",
        "projects/wallposts/text": "projects/wallposts/text",
        "organizations/manage": "organizations/manage",
        "organizations/addresses/manage": "organizations/addresses/manage",
        "organizations/documents/manage": "organizations/documents/manage",
        "projects/ambassadors/manage": "projects/ambassadors/manage",
        "projects/budgetlines/manage": "projects/budgetlines/manage",
        "users/activate": "users/activate",
        "users/passwordset": "users/passwordset",
        "homepage": "homepage",
        "pages/contact": "pages/contact"
    }
});

// Assigning plurals for model properties doesn't seem to work with extend, it does this way:
App.Adapter.configure("plurals", {
    "address": "addresses"
});

App.Adapter.map(
    'App.Payment', {
        availablePaymentMethods: { readOnly: true }
    },
    'App.Order', {
        total: { readOnly: true }
    }
);


App.ApplicationController = Ember.Controller.extend({
    needs: ['currentUser', 'currentOrder', 'myProjectList'],
    display_message: false,

    news: function() {
        return App.NewsPreview.find({language: App.get('language')});
    }.property(),

    displayMessage: (function() {
        if (this.get('display_message') == true) {
            Ember.run.later(this, function() {
                this.hideMessage();
            }, 10000);
        }
    }).observes('display_message'),

    hideMessage: function() {
        this.set('display_message', false);
    },
    currentPathChanged: function() {
        // window.location gets updated later in the current run loop, so we will
        // wait until the next run loop to inspect its value and make the call
        // to track the page view
        Ember.run.next(function() {
            setCookie('hash_compat', window.location.hash)
        });
    }.observes('currentPath')
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


App.Adapter.map('App.Quote', {
    user: {embedded: 'load'}
});
App.Adapter.map('App.ContactMessage', {
    author: {embedded: 'load'}
});

App.Store = DS.Store.extend({
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

App.Router.reopen({
    location: 'hashbang'
});

App.Router.reopen({
    /**
     * Tracks pageviews if google analytics is used
     * Source: http://www.randomshouting.com/2013/05/04/Ember-and-Google-Analytics.html
     */
    didTransition: function(infos) {
        this._super(infos);
        if (window._gaq === undefined) { return; }
        
        Ember.run.next(function(){
            _gaq.push(['_trackPageview', window.location.hash.substr(1)]);
        });
    }
});

App.Router.reopen({
    didTransition: function(infos) {
        this._super(infos);
        Ember.run.next(function() {
            // the meta module will now go trough the routes and look for data
            App.meta.trigger('reloadDataFromRoutes');
        });
    }
});

App.Router.map(function() {

    this.resource('language', {path:'/:lang'});

    // Fix for Facebook logins
    this.route("home", { path: "_=_" });

    this.route("home", { path: "/" });

    this.resource('error', {path: '/error'}, function() {
        this.route('notFound', {path: '/not-found'});
        this.route('notAllowed', {path: '/not-allowed'});
    });
});


DS.Model.reopen({
    meta_data: DS.attr('object')
});


Em.Route.reopen({
    meta_data: function(){
        return this.get('context.meta_data');
    }.property('context.meta_data')
});


App.ApplicationRoute = Em.Route.extend({

//    setupController: function(controller, model) {
//        this.controllerFor('myProjectList').set('model', App.MyProject.find());
//        this._super(controller, model);
//    },

    actions: {
        selectLanguage: function(language) {
            var user = App.CurrentUser.find('current');
            if (!user.get('id_for_ember')) {
                if (language == App.get('language')) {
                    // Language already set. Don't do anything;
                    return true;
                } else {
                    document.location = '/' + language + document.location.hash;
                }
            }

            App.UserSettings.find(App.CurrentUser.find('current').get('id_for_ember')).then(function(settings){
                if (language == App.get('language')) {
                    // Language already set. Don't do anything;
                    return true;
                }

                if (settings.get('id')) {
                    settings.save();
                }
                var languages = App.get('interfaceLanguages');
                for (i in languages) {
                    // Check if the selected language is available.
                    if (languages[i].code == language) {
                        if (settings.get('id')) {
                            settings.set('primary_language', language);
                        }
                        settings.on('didUpdate', function(){
                            document.location = '/' + language + document.location.hash;
                        });
                        settings.save();
                        return true;
                    }
                }
                language = 'en';
                if (settings.get('id')) {
                    settings.set('primary_language', language);
                }

                settings.on('didUpdate', function(){
                    document.location = '/' + language + document.location.hash;
                });
                settings.save();
                return true;
            });
            return true;
        },

        openModal: function(name) {
            var route = this;
            $('#' + name).addClass('modal-active').removeClass('is-hidden');
            $('body').append('<div class="modal-backdrop"></div>');
            $('.modal-backdrop').click(function(){
                route.send('closeAllModals');
            });
        },

        closeAllModals: function(){
            $('.modal-active').removeClass('modal-active').addClass('is-hidden');
            $('.modal-backdrop').fadeOut(200, function(){
                this.remove();
            });
        },

        openInBigBox: function(name, context) {
            // Get the controller or create one
            var controller = this.controllerFor(name);
            controller.set('model', context);

            // Get the view. This should be defined.
            var view = App[name.classify() + 'View'].create();
            view.set('controller', controller);

            var modalPaneTemplate = ['<div class="modal-wrapper"><a class="modal-close" rel="close">&times;</a>{{view view.bodyViewClass}}</div>'].join("\n");

            Bootstrap.ModalPane.popup({
                classNames: ['modal', 'large'],
                defaultTemplate: Em.Handlebars.compile(modalPaneTemplate),
                bodyViewClass: view,
                secondary: 'Close'
            });

        },

        openInBox: function(name, context) {
            // Get the controller or create one
            var controller = this.controllerFor(name);
            if (context) {
                controller.set('model', context);
            }

            // Get the view. This should be defined.
            var view = App[name.classify() + 'View'].create();
            view.set('controller', controller);

            var modalPaneTemplate = ['<div class="modal-wrapper"><a class="modal-close" rel="close">&times;</a>{{view view.bodyViewClass}}</div>'].join("\n");

            Bootstrap.ModalPane.popup({
                classNames: ['modal'],
                defaultTemplate: Em.Handlebars.compile(modalPaneTemplate),
                bodyViewClass: view
            });

        },
        showProject: function(project_id) {
            var route = this;
            App.Project.find(project_id).then(function(project) {
                route.transitionTo('project', project);
            });
        },
        showProjectTaskList: function(project_id) {
            var route = this;
            App.Project.find(project_id).then(function(project) {
                route.transitionTo('project', project);
                route.transitionTo('projectTaskList');
            });
        },
        showTask: function(task) {
            var route = this;
            App.Task.find(task.get('id')).then(function(task) {
                App.Project.find(task.get('project.id')).then(function(project) {
                    route.transitionTo('project', project);
                    route.transitionTo('projectTask', task);
                });
            });
        },
        showNews: function(news_id) {
            var route = this;
            App.News.find(news_id).then(function(news) {
                route.transitionTo('newsItem', news);
            });
        },
        showPage: function(page_id) {
            var route = this;
            App.Page.find(page_id).then(function(page) {
                route.transitionTo('page', page);
            });
        },

        addDonation: function (project) {
            var route = this;
            App.CurrentOrder.find('current').then(function(order) {
                var store = route.get('store');
                if (order.get('donations').anyBy('project', project)) {
                   // Donation for this already exists in this order.
                } else {
                    var donation = store.createRecord(App.CurrentOrderDonation);
                    donation.set('project', project);
                    donation.set('order', order);
                    donation.save();
                }
                route.transitionTo('currentOrder.donationList');
            });
        }
    },

    urlForEvent: function(actionName, context) {
        return "/nice/stuff"
    }
});

App.UserIndexRoute = Em.Route.extend({
    beforeModel: function() {
        this.transitionTo('userProfile');
    }
});


// TODO Delete this Route when we implement Order history.
App.UserRoute = Em.Route.extend({
    setupController: function(controller, model) {
        this._super(controller, model);

        return App.RecurringDirectDebitPayment.find({}).then(function(recurringPayments) {
            controller.set('showPaymentsTab', recurringPayments.get('length') > 0)
        });
    }
});

/* Home Page */

App.HomeRoute = Em.Route.extend({
    model: function(params) {
        return App.HomePage.find(App.get('language'));
    },

    setupController: function(controller, model) {
        this._super(controller, model);
        controller.set('projectIndex', 0).loadProject();
        controller.set('quoteIndex', 0).loadQuote();
    }
});

/* Components */

App.BbModalComponent = Ember.Component.extend({
    classNames: ['is-hidden'],
    actions: {
        close: function() {
            this.$().removeClass('modal-active').addClass('is-hidden');
            $('.modal-backdrop').fadeOut(200, function(){
                this.remove();
            });
        }
    }
});


/* Views */

App.LanguageView = Em.View.extend({
    templateName: 'language',
    classNameBindings: ['isSelected:active'],
    isSelected: function(){
        if (this.get('content.code') == App.language) {
            return true;
        }
        return false;
    }.property('content.code')

});

App.LanguageSwitchView = Em.CollectionView.extend({
    tagName: 'ul',
    classNames: ['nav-language'],
    content: App.interfaceLanguages,
    itemViewClass: App.LanguageView
});


App.ApplicationView = Em.View.extend({
    elementId: 'site'
});


