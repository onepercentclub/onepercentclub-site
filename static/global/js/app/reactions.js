
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
        var transaction = this.get('store').transaction();
        var reaction =  transaction.createRecord(App.WallPostReaction);
        this.set('newReaction', reaction);
        this.set('transaction', transaction);
    },

    addReaction: function() {
        var reaction = this.get('newReaction');
        // Set the wallpost that this reaction is related to.
        reaction.set('wallpost', this.get('target.model'));
        reaction.set('created', new Date());
        var controller = this;
        reaction.on('didCreate', function(record) {
            controller.createNewReaction();
        });
        reaction.on('becameInvalid', function(record) {
            controller.createNewReaction();
            controller.set('errors', record.get('errors'));
            record.deleteRecord();
        });

        this.get('transaction').commit();
        // TODO: remove is-selected class from form
    }
});


/*
 Views
 */


App.WallPostReactionView = Em.View.extend({
    templateName: 'wallpost_reaction',
    tagName: 'li',
    classNames: ['initiator'],

    deleteReaction: function() {
        var view = this;
        Bootstrap.ModalPane.popup({
            heading: gettext("Really?"),
            message: gettext("Are you sure you want to delete this reaction?"),
            primary: gettext("Yes"),
            secondary: gettext("Cancel"),
            callback: function(opts, e) {
                e.preventDefault();
                if (opts.primary) {
                    view.$().fadeOut(500, function() {
                        view.get('controller').deleteRecordOnServer()
                    });
                }
            }
        });
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

