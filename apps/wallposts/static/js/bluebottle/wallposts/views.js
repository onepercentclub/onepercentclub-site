
/*
 Views
 */

App.WallPostView = Em.View.extend({

    templateName: 'wallPost',

    didInsertElement: function(){
        var view = this;
        view.$().hide();
        // Give it some time to really render...
        // Hack to make sure photo viewer works for new wallposts
        Em.run.next(function(){

            // slideDown has weird behaviour on Task Wall with post not appearing.
            // view.$().slideDown(500);
            view.$().fadeIn(500);

            view.$('.photo-viewer a').colorbox({
                rel: this.toString(),
                next: '<span class="flaticon solid right-2"></span>',
                previous: '<span class="flaticon solid left-2"></span>',
                close: 'x'
            });
        });
    },

    actions: {
        deleteWallPost: function() {
            var view = this;
            var wallpost = this.get('controller.model');
            Bootstrap.ModalPane.popup({
                heading: gettext("Really?"),
                message: gettext("Are you sure you want to delete this comment?"),
                primary: gettext("Yes"),
                secondary: gettext("Cancel"),
                callback: function(opts, e) {
                    e.preventDefault();
                    if (opts.primary) {
                        view.$().fadeOut(500, function() {
                            wallpost.deleteRecord();
                            wallpost.save();
                        });
                    }
                }
            });
        }
    }
});


App.SystemWallPostView = App.WallPostView.extend({
    templateName: 'systemWallPost'
});


App.MediaWallPostView = App.WallPostView.extend({
});


App.TextWallPostNewView = Em.View.extend({
    templateName: 'textWallPostNew',
    tagName: 'form',
    elementId: 'wallpost-form'
});

App.MediaWallPostNewView = App.TextWallPostNewView.extend({
    templateName: 'mediaWallPostNew'
});


App.ProjectMediaWallPostNewView = App.MediaWallPostNewView.extend({});
App.ProjectTextWallPostNewView = App.TextWallPostNewView.extend({});

App.FundRaiserTextWallPostNewView = App.TextWallPostNewView.extend({});
App.FundRaiserMediaWallPostNewView = App.MediaWallPostNewView.extend({});

App.TaskMediaWallPostNewView = App.MediaWallPostNewView.extend({});
App.TaskTextWallPostNewView = App.TextWallPostNewView.extend({});


/* Reactions */

App.WallPostReactionView = Em.View.extend({
    templateName: 'wallpost_reaction',
    //tagName: 'li',
    //classNames: ['reaction'],
    actions: {
        deleteReaction: function() {
            var view = this;
            var model = this.get('controller.model');
            Bootstrap.ModalPane.popup({
                heading: gettext("Really?"),
                message: gettext("Are you sure you want to delete this reaction?"),
                primary: gettext("Yes"),
                secondary: gettext("Cancel"),
                callback: function(opts, e) {
                    e.preventDefault();
                    if (opts.primary) {
                        view.$().fadeOut(500, function() {
                            model.deleteRecord();
                            model.save();
                        });
                    }
                }
            });
        }
    }
});


App.WallPostReactionListView = Em.View.extend({
    templateName: 'wallpost_reaction_list',

    submit: function(e) {
        e.preventDefault();
        this.get('controller').addReaction();
    },

    didInsertElement: function(e) {
        var view = this;
        view.$('textarea').focus(function(e) {
            view.$('.reaction-form').addClass('is-selected');
        }).blur(function(e) {
            if (!$(this).val()) {
                // textarea is empty or contains only white-space
                view.$('.reaction-form').removeClass('is-selected');
            }
        });
    }
});

