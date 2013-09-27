
/*
 Models
 */

App.WallPostReaction = DS.Model.extend({
    url: 'wallposts/reactions',

    text: DS.attr('string'),
    author: DS.belongsTo('App.UserPreview'),
    created: DS.attr('date'),
    wallpost: DS.belongsTo('App.WallPost')
});


/*
 Controllers
 */

App.WallPostReactionController = Em.ObjectController.extend(App.IsAuthorMixin, App.DeleteModelMixin, {
    needs: ['currentUser']
});


App.WallPostReactionListController = Em.ArrayController.extend({
    needs: ['currentUser'],

    init: function() {
        this._super();
        this.createNewReaction();
    },

    createNewReaction: function() {
        var store = this.get('store');
        var reaction =  store.createRecord(App.WallPostReaction);
        this.set('newReaction', reaction);
    },

    addReaction: function() {
        var reaction = this.get('newReaction');
        // Set the wallpost that this reaction is related to.
        reaction.set('wallpost', this.get('target.model'));
        reaction.set('created', new Date());
        var controller = this;
        reaction.on('didCreate', function(record) {
            controller.createNewReaction();
            // remove is-selected from all input roms
            $('form.is-selected').removeClass('is-selected');
        });
        reaction.on('becameInvalid', function(record) {
            controller.createNewReaction();
            controller.set('errors', record.get('errors'));
            record.deleteRecord();
        });
        reaction.save();
    }
});


/*
 Views
 */


App.WallPostReactionView = Em.View.extend({
    templateName: 'wallpost_reaction',
    tagName: 'li',
    classNames: ['initiator'],
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

