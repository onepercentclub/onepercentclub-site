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


// Create a mock 'File' class so things won't break to awfully in IE8&9
// FIXME: Use a polyfill for this!!
// https://github.com/francois2metz/html5-formdata
if (Em.isNone(File)) {
    var File = function(){};
}

Em.TextField.reopen({
    // Update attributeBinding with 'step' and 'multiple'
    attributeBindings: ['type', 'value', 'size', 'step', 'multiple']
});


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
                    if (window.console) {
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
                    if (window.console) {
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

/*

For now we included all hbs templates in index.html.


// Now halt the App because we first want to load all templates
App.deferReadiness();

App.loadTemplates = function() {
    var language = window.location.pathname.split('/')[1];
    // TODO: Make sure to avoid race conditions. See if we can dynamically load this as needed.
    // Now that we know the language we can load the handlebars templates.
    var readyCount = 0;
    var templates = Em.A(['users', 'homepage', 'wallposts', 'reactions', 'tasks', 'projects', 'orders', 'utils', 'blogs']);
    templates.forEach(function(template) {
        //loadTemplates(this.templates);
        var hash = {};
        hash.url = '/' + language + '/templates/' + template + '.hbs';
        hash.type = 'GET';
        hash.contentType = 'application/json';
        hash.success = function(data) {
            // Iterate through handlebar tags
            $(data).filter('script[type="text/x-handlebars"]').each(function() {
                var templateName = $(this).attr('data-template-name');
                var raw = $(this).html();
                Em.TEMPLATES[templateName] = Em.Handlebars.compile(raw);
            });
            readyCount++;
            if (readyCount == templates.length) {
                App.advanceReadiness();
            }
        };
        hash.error = function(jqXHR, textStatus, errorThrown) {
            throw errorThrown + ' ' + hash.url;
        };
        jQuery.ajax(hash);

    });
};

App.loadTemplates();
*/

/*
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
    campaign: {embedded: 'load'},
    plan: {embedded: 'load'},
    country: {embedded: 'load'}
});
App.Adapter.map('App.ProjectPreview', {
    campaign: {embedded: 'load'},
    country: {embedded: 'load'}
});
App.Adapter.map('App.DonationPreview', {
    project: {embedded: 'load'},
    member: {embedded: 'load'}
});
App.Adapter.map('App.WallPost', {
    author: {embedded: 'load'},
    photos: {embedded: 'load'},
    reactions: {embedded: 'load'}
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
App.Adapter.map('App.TaskWallPost', {
    author: {embedded: 'load'},
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
App.Adapter.map('App.Task', {
    author: {embedded: 'load'},
    tags: {embedded: 'always'},
    members: {embedded: 'load'},
    files: {embedded: 'load'}
});
App.Adapter.map('App.TaskPreview', {
    author: {embedded: 'load'},
    project: {embedded: 'load'}
});
App.Adapter.map('App.TaskMember', {
    member: {embedded: 'load'}
});
App.Adapter.map('App.TaskFile', {
    author: {embedded: 'load'}
});
App.Adapter.map('App.ProjectPlan', {
    tags: {embedded: 'load'},
    country: {embedded: 'load'}
});
App.Adapter.map('App.ProjectPitch', {
    tags: {embedded: 'load'},
    country: {embedded: 'load'}
});
App.Adapter.map('App.MyProjectPlan', {
    ambassadors: {embedded: 'load'},
    budgetLines: {embedded: 'load'},
    tags: {embedded: 'always'}
});
App.Adapter.map('App.MyProjectPitch', {
    tags: {embedded: 'always'}
});
App.Adapter.map('App.MyOrganization', {
    addresses: {embedded: 'both'},
    documents: {embedded: 'load'}
});
App.Adapter.map('App.MyOrganizationDocument', {
    file: {embedded: 'load'}
});

App.Adapter.map('App.Quote', {
    user: {embedded: 'load'}
});

App.Adapter.map('App.News', {
    author: {embedded: 'load'}
});
App.Adapter.map('App.ContactMessage', {
    author: {embedded: 'load'}
});

App.Adapter.map('App.HomePage', {
    projects: {embedded: 'load'},
    slides: {embedded: 'load'},
    quotes: {embedded: 'load'},
    impact: {embedded: 'load'}
});
App.Adapter.map('App.PartnerOrganization', {
    projects: {embedded: 'load'}
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

App.Router.map(function() {

    this.resource('language', {path:'/:lang'});

    // Fix for Facebook logins
    this.route("home", { path: "_=_" });

    this.route("home", { path: "/" });

    this.resource('projectList', {path: '/projects'}, function() {
        this.route('new');
        this.route('search');
    });

    this.resource('error', {path: '/error'}, function() {
        this.route('notFound', {path: '/not-found'});
        this.route('notAllowed', {path: '/not-allowed'});
    });


    this.resource('news', {path: '/news'}, function() {
        this.resource('newsItem', {path: '/:news_id'});
    });

    this.resource('page', {path: '/pages/:page_id'});
    this.resource('contactMessage', {path: '/contact'});

    this.resource('project', {path: '/projects/:project_id'}, function() {
        this.resource('projectPlan', {path: '/plan'});
        this.resource('projectTaskList', {path: '/tasks'});
        this.resource('projectTaskNew', {path: '/tasks/new'});
        this.resource('projectTask', {path: '/tasks/:task_id'});
        this.resource('projectTaskEdit', {path: '/tasks/:task_id/edit'});
    });

    this.resource('currentOrder', {path: '/support'}, function() {
        this.route('donationList', {path: '/donations'});
        this.route('voucherList', {path: '/giftcards'});
        this.resource('paymentProfile', {path: '/details'});
        this.resource('paymentSignup', {path: '/signup'});
        this.resource('paymentSelect', {path: '/payment'}, function() {
            this.route('paymentError', {path: '/error'});
            this.resource('recurringDirectDebitPayment', {path: '/recurring'});
        });
    });

    this.resource('orderThanks', {path: '/support/thanks/:order_id'});
    this.resource('recurringOrderThanks', {path: '/support/monthly/thanks'});

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

    this.resource('taskList', {path: '/tasks'});

    accounts_router.call(this);

    // this.resource('signup');

    // this.resource('user', {path: '/member'}, function() {
    //     this.resource('userProfile', {path: '/profile/'});
    //     this.resource('userSettings', {path: '/settings'});
    //     this.resource('userOrders', {path: '/orders'});
    // });

    // this.route('userActivate', {path: '/activate/:activation_key'});
    // this.resource('passwordReset', {path: '/passwordreset/:reset_token'});

    this.resource('myProject', {path: '/my/projects/:my_project_id'}, function() {
        this.resource('myProjectPlan', {path: 'plan'}, function() {
            this.route('index');
            this.route('basics');
            this.route('location');
            this.route('description');
            this.route('media');

            this.route('organisation');
            this.route('legal');
            this.route('ambassadors');

            this.route('bank');
            this.route('campaign');
            this.route('budget');

            this.route('submit');

        });

        this.resource('myProjectPlanReview', {path: 'plan/review'});
        this.resource('myProjectPlanApproved', {path: 'plan/approved'});
        this.resource('myProjectPlanRejected', {path: 'plan/rejected'});

        this.resource('myProjectPitch', {path: 'pitch'}, function() {
            this.route('index');
            this.route('basics');
            this.route('location');
            this.route('media');

            this.route('submit');
        });
        this.resource('myProjectPitchReview', {path: 'pitch/review'});
        this.resource('myProjectPitchApproved', {path: 'pitch/approved'});
        this.resource('myProjectPitchRejected', {path: 'pitch/rejected'});

        this.resource('myProjectCampaign', {path: 'campaign'});

    });

    this.resource('myPitchNew', {path: '/my/pitch/new'});
    this.resource('myProjectList', {path: '/my/projects'});
    this.resource('partner', {path: '/pp/:partner_organization_id'});

});


App.ApplicationRoute = Em.Route.extend({

    setupController: function(controller, model) {
        this.controllerFor('myProjectList').set('model', App.MyProject.find());

        // FIXME: This totaly breaks donation flow because the unloadRecord trick in CurrrenOrderRoute.model(), somehow.
        // For now ignore. Donation reminder will only be there if you donated during this session...
        //this.controllerFor('currentOrder').set('model',  App.CurrentOrder.find('current'));

        this._super(controller, model);
    },


    actions: {
        selectLanguage: function(language) {
            var user = App.CurrentUser.find('current');
            if (!user.get('id_for_ember')) {
                if (language == App.get('language')) {
                    // Language already set. Don't do anything;
                    return true;
                }
                document.location = '/' + language + document.location.hash;
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

        openInBigBox: function(name, context) {
            // Get the controller or create one
            var controller = this.controllerFor(name);
            controller.set('model', context);

            // Get the view. This should be defined.
            var view = App[name.classify() + 'View'].create();
            view.set('controller', controller);

            var modalPaneTemplate = ['<div class="modal-body"><a class="close" rel="close">&times;</a>{{view view.bodyViewClass}}</div>'].join("\n");

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

            var modalPaneTemplate = ['<div class="modal-body"><a class="close" rel="close">&times;</a>{{view view.bodyViewClass}}</div>'].join("\n");

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
                window.scrollTo(0, 0);
            });
        },
        showPage: function(page_id) {
            var route = this;
            App.Page.find(page_id).then(function(page) {
                route.transitionTo('page', page);
                window.scrollTo(0, 0);
            });
        },

        addDonation: function (project) {
            var route = this;
            App.CurrentOrder.find('current').then(function(order) {
                var store = route.get('store');
                var donation = store.createRecord(App.CurrentOrderDonation);
                donation.set('project', project);
                donation.set('order', order);
                donation.save();
                route.transitionTo('currentOrder.donationList');
            });
        }
    },

    urlForEvent: function(actionName, context) {
        return "/nice/stuff"
    }
});


/**
 * Project Routes
 */

App.ProjectRoute = Em.Route.extend({
    model: function(params) {
        var page =  App.Project.find(params.project_id);
        var route = this;
        page.on('becameError', function() {
            //route.transitionTo('error.notFound');
            route.transitionTo('projectList');
        });
        return page;
    },

    setupController: function(controller, project) {
        this._super(controller, project);

        // Set the controller to show Project Supporters
        var projectSupporterListController = this.controllerFor('projectSupporterList');
        projectSupporterListController.set('supporters', App.DonationPreview.find({project: project.get('id')}));
        projectSupporterListController.set('page', 1);
        projectSupporterListController.set('canLoadMore', true);
    }
});


// This is the 'ProjectWallPostListRoute'
App.ProjectIndexRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('project');
    },

    setupController: function(controller, model) {
        // Empty the items and set page to 0 if project changes so we don't show wall posts from previous project
        if (this.get('model_id') != model.get('id')) {
            controller.set('items', Em.A());
            controller.set('page', 0);
        }
        this.set('model_id', model.get('id'));
        this._super(controller, model.get('wallposts'));
    }
});


App.ProjectPlanRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('project').get('plan');
    }
});


// Tasks

App.ProjectTaskListRoute = Em.Route.extend({
    model: function(params) {
        return Em.A();
    },

    setupController: function(controller, model) {
        this._super(controller, model);
        var project = this.modelFor('project');
        var tasks = App.Task.find({project: project.get('id')});
        tasks.addObserver('isLoaded', function() {
            tasks.forEach(function(record) {
                if (record.get('isLoaded')) {
                    controller.get('content').pushObject(record);
                }
            });
        });
    }
});


App.ProjectTaskRoute = Em.Route.extend({
    model: function(params) {
        return App.Task.find(params.task_id);
    },
    setupController: function(controller, model) {
        this._super(controller, model);

        var wallPostController = this.controllerFor('taskWallPostList');
        wallPostController.set('model', model.get('wallposts'));
        wallPostController.set('items', Em.A());
        wallPostController.set('page', 0);
    },
    actions: {
        applyForTask: function(task) {
            var route = this;
            var store = route.get('store');
            var taskMember = store.createRecord(App.TaskMember);
            var view = App.TaskMemberApplyView.create();


            Bootstrap.ModalPane.popup({
                heading: gettext('Apply for task'),
                bodyViewClass: view,
                primary: gettext('Apply'),
                secondary: gettext('Cancel'),
                callback: function(opts, e) {
                    e.preventDefault();
                    if (opts.primary) {
                        taskMember.set('task', task);
                        taskMember.set('motivation', view.get('motivation'));
                        taskMember.set('created', new Date());
                        taskMember.save();
                    }
                }
            });
        },
        uploadFile: function(task) {
            var route = this;
            var controller = this.controllerFor('taskFileNew');
            var view = App.TaskFileNewView.create();
            view.set('controller', controller);
            var store = route.get('store');
            var file = store.createRecord(App.TaskFile);
            controller.set('model', file);
            file.set('task', task);

            Bootstrap.ModalPane.popup({
                classNames: ['modal', 'large'],
                headerViewClass: Ember.View.extend({
                    tagName: 'p',
                    classNames: ['modal-title'],
                    template: Ember.Handlebars.compile('{{view.parentView.heading}}')
                }),
                heading: task.get('title'),
                bodyViewClass: view,
                primary: 'Save',
                secondary: 'Cancel',
                callback: function(opts, e) {
                    e.preventDefault();
                    if (opts.primary) {
                        file.save();
                    }
                    if (opts.secondary) {
                        file.deleteRecord();
                    }
                }
            });
        },
        showMoreWallPosts: function() {
            var controller = this.get('controller');
            var wallPostController = this.controllerFor('taskWallPostList');
            wallPostController.set('canLoadMore', false);
            var page = wallPostController.incrementProperty('page');
            var task = controller.get('model');
            var wps = App.TaskWallPost.find({task: task.get('id'), page: page});
            wps.addObserver('isLoaded', function() {
                wps.forEach(function(record) {
                    if (record.get('isLoaded')) {
                        wallPostController.get('content').pushObject(record);
                    }
                });
                wallPostController.set('canLoadMore', true);
            });
        },
        editTaskMember: function(taskMember) {
            var route = this;
            var controller = this.controllerFor('taskMemberEdit');
            controller.set('model', taskMember);
            var view = App.TaskMemberEdit.create();
            view.set('controller', controller);

            Bootstrap.ModalPane.popup({
                headerViewClass: Ember.View.extend({
                    tagName: 'p',
                    classNames: ['modal-title'],
                    template: Ember.Handlebars.compile('{{view.parentView.heading}}')
                }),
                heading: taskMember.get('member.full_name'),
                bodyViewClass: view,
                primary: 'Save',
                secondary: 'Cancel',
                callback: function(opts, e) {
                    e.preventDefault();
                    if (opts.primary) {
                        taskMember.save();
                    }
                    if (opts.secondary) {
                        taskMember.rollback();
                    }
                }
            });
        },
        stopWorkingOnTask: function(task) {
            alert('Not implemented. Sorry!');
        }
    }
});


App.ProjectTaskNewRoute = Em.Route.extend({

    setupController: function(controller, model) {
        this._super(controller, model);
        var store = this.get('store');
        var model = store.createRecord(App.Task);
        controller.set('content', model);
    }
});


App.ProjectTaskEditRoute = Em.Route.extend({
    model: function(params) {
        return App.Task.find(params.task_id);
    }
});



/**
 * Current Order Routes
 */

// Redirect to the donations list if somebody tries load '/support'.
App.CurrentOrderIndexRoute = Em.Route.extend({
    redirect: function() {
        this.transitionTo('currentOrder.donationList');
    }
});


App.CurrentOrderRoute = Em.Route.extend({
    model: function(params) {
        return App.CurrentOrder.find('current');
    }
});


App.CurrentOrderDonationListRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('currentOrder').get('donations');
    },

    setupController: function(controller, donations) {
        this._super(controller, donations);
        this.controllerFor('currentOrder').set('isVoucherOrder', false);

        // Set the monthly order.
        App.Order.find({status: 'recurring'}).then(function(recurringOrders) {
            if (recurringOrders.get('length') > 0) {
                controller.set('recurringOrder', recurringOrders.objectAt(0))
            } else {
                controller.set('recurringOrder', null)
            }
        });

        // Set the top three projects
        App.ProjectPreview.find({ordering: 'popularity', phase: 'campaign'}).then(function(projects) {
            controller.set('topThreeProjects', projects.slice(0, 3));
        });

        // set the recurring payment
        App.RecurringDirectDebitPayment.find({}).then(function(recurringPayments) {
            if (recurringPayments.get('length') > 0) {
                controller.set('recurringPayment', recurringPayments.objectAt(0));
            }else {
                controller.set('recurringPayment', null);
            }
        });
    }
});


App.CurrentOrderVoucherListRoute = Em.Route.extend({
    model: function(params) {
        var order = this.modelFor('currentOrder');
        return order.get('vouchers');
    },

    setupController: function(controller, vouchers) {
        this._super(controller, vouchers);
        this.controllerFor('currentOrder').set('isVoucherOrder', true);
    }
});


App.OrderThanksRoute = Em.Route.extend({
    model: function(params) {
        var route = this;
        var order = App.Order.find(params.order_id);
        order.one('becameError', function() {
            route.controllerFor('application').setProperties({
                display_message: true,
                isError: true,
                message_title: "",
                message_content: "Sorry, we can't find your order."
            });
            route.replaceWith('home');
        });
        return order;
    }
});


App.RecurringOrderThanksRoute = Em.Route.extend({
// FIXME: Enable this when we fix the issue with transitioning to this route without a full page reload.
//    beforeModel: function() {
//        if (!this.controllerFor('currentUser').get('isAuthenticated')) {
//            this.transitionTo('home');
//        }
//    },

    model: function(params) {
        return App.Order.find({status: 'recurring'}).then(function(orders) {
            if (orders.get('length') > 0) {
                return orders.objectAt(0);
            }
            this.transitionTo('home');
        });
    },

    setupController: function(controller, order) {
        this._super(controller, order);

        App.RecurringDirectDebitPayment.find({}).then(function(recurringPayments) {
            if (recurringPayments.get('length') > 0) {
                controller.set('recurringPayment', recurringPayments.objectAt(0));
            } else {
                controller.set('recurringPayment', null);
            }
        });

        // Set the top three projects
        App.ProjectPreview.find({ordering: 'popularity', phase: 'campaign'}).then(function(projects) {
            controller.set('topThreeProjects', projects.slice(0, 3));
        });
    }
});


/**
 * Payment for Current Order Routes
 */

App.PaymentProfileRoute = Em.Route.extend({
    beforeModel: function() {
        var order = this.modelFor('currentOrder');
        if (order.get('isVoucherOrder')) {
            if (order.get('vouchers.length') <= 0 ) {
                this.transitionTo('currentOrder.voucherList')
            }
        } else {
            var controller = this.controllerFor('currentOrderDonationList');
            if (controller.get('editingRecurringOrder')) {
                if (controller.get('recurringTotal') == 0 && this.get('recurringTotal') == controller.get('recurringOrder.total')) {
                    this.transitionTo('currentOrder.donationList')
                }
            } else {
                if (!order.get('recurring') && order.get('donations.length') <= 0 ) {
                    this.transitionTo('currentOrder.donationList')
                }
            }
        }

    },

    model: function(params) {
        return App.PaymentProfile.find('current');
    }
});


App.PaymentSignupRoute = Em.Route.extend({
    model: function(params) {
        var model = App.UserCreate.createRecord();
        return App.PaymentProfile.find('current').then(function(profile){
            model.set('email', profile.get('email'));
            model.set('first_name', profile.get('firstName'));
            model.set('last_name', profile.get('lastName'));
            return model;
        });
    }
});


App.PaymentSelectRoute = Em.Route.extend({
    beforeModel: function() {
        var order = this.modelFor('currentOrder');
        if (!order.get('paymentProfileComplete')) {
            this.replaceWith('paymentProfile');
        } else if (order.get('recurring')) {
            this.replaceWith('recurringDirectDebitPayment');
        }
    },

    model: function(params) {
        return App.Payment.find('current');
    }
});


App.PaymentSelectPaymentErrorRoute = Em.Route.extend({
    beforeModel: function() {
        this.controllerFor('currentOrder').setProperties({
            display_message: true,
            isError: true,
            autoHideMessage: false,
            message_content: 'There was an error with your payment. Please try again.'
        });

        var order = this.modelFor('currentOrder');
        if (order.get('isVoucherOrder')) {
            this.replaceWith('currentOrder.voucherList');
        } else {
            this.replaceWith('currentOrder.donationList');
        }
    }
});


App.RecurringDirectDebitPaymentRoute = Em.Route.extend({
    beforeModel: function() {
        var order = this.modelFor('currentOrder');
        if (!order.get('recurring')) {
            this.transitionTo('paymentSelect');
        }
    },

    model: function() {
        var route = this;
        return App.RecurringDirectDebitPayment.find({}).then(function(recordList) {
                var store = route.get('store');
                if (recordList.get('length') > 0) {
                    var record = recordList.objectAt(0);
                    return record;
                } else {
                    return store.createRecord(App.RecurringDirectDebitPayment);
                }
            }
        )
    }
});


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


/**
 * My Projects
 * - Manage your project(s)
 */

App.MyProjectListRoute = Em.Route.extend({
    model: function(params) {
        return App.MyProject.find();
    },
    setupController: function(controller, model) {
        this._super(controller, model);
    }

});


App.MyPitchNewRoute = Em.Route.extend({
    model: function() {
        var store = this.get('store');
        return store.createRecord(App.MyProject);
    }
});


App.MyProjectRoute = Em.Route.extend({
    // Load the Project
    model: function(params) {
        return App.MyProject.find(params.my_project_id);
    }
});


App.MyProjectPitchRoute =  Em.Route.extend({
    model: function(params) {
        return this.modelFor('myProject').get('pitch');
    }
});


App.MyProjectPitchSubRoute = Ember.Route.extend({
    redirect: function() {
        var status = this.modelFor('myProject').get('pitch.status');
        switch(status) {
            case 'submitted':
                this.transitionTo('myProjectPitchReview');
                break;
            case 'rejected':
                this.transitionTo('myProjectPitchRejected');
                break;
            case 'approved':
                this.transitionTo('myProjectPitchApproved');
                break;
        }
    },
    model: function(params) {
        return this.modelFor('myProject').get('pitch');
    },
    setupController: function(controller, model) {
        this._super(controller, model);
        controller.startEditing();
    },
    exit: function() {
        if (this.get('controller')) {
            this.get('controller').stopEditing();
        }
    }

});


App.MyProjectPitchBasicsRoute = App.MyProjectPitchSubRoute.extend({});
App.MyProjectPitchLocationRoute = App.MyProjectPitchSubRoute.extend({});
App.MyProjectPitchMediaRoute = App.MyProjectPitchSubRoute.extend({});
App.MyProjectPitchSubmitRoute = App.MyProjectPitchSubRoute.extend({});

App.MyProjectPitchIndexRoute =  Em.Route.extend({
    redirect: function() {
        var status = this.modelFor('myProject').get('pitch.status');
        switch(status) {
            case 'submitted':
                this.transitionTo('myProjectPitchReview');
                break;
            case 'rejected':
                this.transitionTo('myProjectPitchRejected');
                break;
            case 'approved':
                this.transitionTo('myProjectPitchApproved');
                break;
        }
    },
    model: function(params) {
        return this.modelFor('myProject').get('pitch');
    }
});


App.MyProjectPitchReviewRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('myProject').get('pitch');
    }
});


// My ProjectPlan routes

App.MyProjectPlanRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('myProject').get('plan');
    }
});

App.MyProjectPlanSubRoute = Em.Route.extend({
    redirect: function() {
        var status = this.modelFor('myProject').get('plan.status');
        switch(status) {
            case 'submitted':
                this.transitionTo('myProjectPlanReview');
                break;
            case 'rejected':
                this.transitionTo('myProjectPlanRejected');
                break;
            case 'approved':
                this.transitionTo('myProjectPlanApproved');
                break;
        }
    },

    model: function(params) {
        return this.modelFor('myProject').get('plan');
    },

    setupController: function(controller, model) {
        this._super(controller, model);
        controller.startEditing();
    },

    exit: function() {
        if (this.get('controller')) {
            this.get('controller').stopEditing();
        }
    }
});

App.MyProjectPlanBasicsRoute = App.MyProjectPlanSubRoute.extend({});
App.MyProjectPlanDescriptionRoute = App.MyProjectPlanSubRoute.extend({});
App.MyProjectPlanLocationRoute = App.MyProjectPlanSubRoute.extend({});
App.MyProjectPlanMediaRoute = App.MyProjectPlanSubRoute.extend({});
App.MyProjectPlanAmbassadorsRoute = App.MyProjectPlanSubRoute.extend({});
App.MyProjectPlanSubmitRoute = App.MyProjectPlanSubRoute.extend({});

App.MyProjectPlanCampaignRoute = App.MyProjectPlanSubRoute.extend({});
App.MyProjectPlanBudgetRoute = App.MyProjectPlanSubRoute.extend({});

App.MyProjectPlanOrganisationRoute = App.MyProjectPlanSubRoute.extend({
    setupController: function(controller, model) {
        this._super(controller, model);
        controller.set('organizations', App.MyOrganization.find());
    }
});

App.MyProjectPlanBankRoute = App.MyProjectPlanSubRoute.extend({});


App.MyProjectPlanLegalRoute = App.MyProjectPlanSubRoute.extend({});


App.MyProjectPlanIndexRoute = Ember.Route.extend({
    redirect: function() {
        var status = this.modelFor('myProject').get('plan.status');
        switch(status) {
            case 'submitted':
                this.transitionTo('myProjectPlanReview');
                break;
            case 'rejected':
                this.transitionTo('myProjectPlanRejected');
                break;
            case 'approved':
                this.transitionTo('myProjectPlanApproved');
                break;
        }
    },

    model: function(params) {
        return this.modelFor('myProject').get('plan');
    }
});


App.MyProjectPlanReviewRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('myProject').get('plan');
    }
});

App.MyProjectCampaignRoute = Em.Route.extend({
    model: function(params) {
        return this.modelFor('myProject');
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


/* Static Pages */

App.PageRoute = Em.Route.extend({
    model: function(params) {
        var page =  App.Page.find(params.page_id);
        var route = this;
        page.on('becameError', function() {
            route.transitionTo('error.notFound');
        });
        return page;
    }
});


/* Blogs & News */

App.NewsItemRoute = Em.Route.extend({
    model: function(params) {
        var newsItem =  App.News.find(params.news_id);
        var route = this;
        newsItem.on('becameError', function() {
            route.transitionTo('error.notFound');
        });
        return newsItem;
    }
});


App.NewsRoute = Em.Route.extend({
    model: function(params) {
        return App.NewsPreview.find({language: App.get('language')});
    }
});


App.NewsIndexRoute = Em.Route.extend({
    model: function(params) {
        return App.NewsPreview.find({language: App.get('language')});
    },
    // Redirect to the latest news item
    setupController: function(controller, model) {
        this.send('showNews', model.objectAt(0).get('id'));
    }
});

/* Contact Page */

App.ContactMessageRoute = Em.Route.extend({
    model: function(params) {
        var store = this.get('store');
        return store.createRecord(App.ContactMessage);
    },
    setupController: function(controller, model) {
        window.scrollTo(0, 0);
        this._super(controller, model);
        controller.startEditing();
    },

    exit: function() {
        if (this.get('controller')) {
            this.get('controller').stopEditing();
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

