
/*
 Models
 */

App.WallPostReaction = DS.Model.extend({
    url: 'wallposts/reactions',

    text: DS.attr('string'),
    author: DS.belongsTo('App.Member'),
    created: DS.attr('string'),
    timesince: DS.attr('string'),
    // We need wallpost_id to create reactions in the API.
    // This can't be a calculated property because calculated properties aren't part of the API calls.
    wallpost_id: DS.attr('number'),
    wallpost: DS.belongsTo('App.ProjectWallPost')
});


/*
 Controllers
 */

App.WallPostReactionController = Em.ObjectController.extend(App.IsAuthorMixin, {
    needs: ['currentUser']
});


App.WallPostReactionListController = Em.ArrayController.extend({
    // This empty controller needs to be here because it's listed in the 'needs' property of
    // App.ProjectWallPostController and Ember doesn't auto-generate controllers in this case.
});


App.WallPostReactionNewController = Em.ObjectController.extend({
    needs: ['currentUser'],

    init: function() {
        this._super();
        this.createNewReaction();
    },

    createNewReaction: function() {
        var transaction = App.store.transaction();
        var reaction =  transaction.createRecord(App.WallPostReaction);
        this.set('content', reaction);
        this.set('transaction', transaction);
    },

    addReaction: function() {
        var reaction = this.get('content');
        reaction.set('wallpost_id', this.get('currentWallpost.id'));
        // Set the wallpost so the list gets updated in the view
        reaction.set('wallpost', this.get('currentWallpost'));

        var controller = this;
        reaction.on('didCreate', function(record) {
            controller.createNewReaction();
        });
        reaction.on('becameInvalid', function(record) {
            controller.createNewReaction();
            controller.set('content.errors', record.get('errors'));
            record.deleteRecord();
        });

        this.get('transaction').commit();
    }
});


/*
 Views
 */

App.WallPostReactionNewView = Em.View.extend({
    templateName: 'wallpost_reaction_new',
    tagName: 'form',
    classNames: ['reaction-form'],

    submit: function(e) {
        e.preventDefault();
        this.get('controller').addReaction();
    },

    didInsertElement: function(e) {
        this.$('textarea').focus(function(e) {
            $(this).parents('.reaction-form').addClass('is-selected');
        });
        this.$(this).blur(function(e) {
            $(this).parent('.reaction-form').removeClass('is-selected');
        });
    }
});


App.WallPostReactionView = Em.View.extend({
    templateName: 'wallpost_reaction',
    tagName: 'li',
    classNames: ['initiator'],

    deleteReaction: function() {
        if (confirm("Delete this reaction?")) {
            var transaction = App.store.transaction();
            var reaction = this.get('controller.content');
            transaction.add(reaction);
            this.$().fadeOut(500, function() {
                reaction.deleteRecord();
                transaction.commit();
            });
        }
    }
});


App.WallPostReactionListView = Em.View.extend({
    templateName: 'wallpost_reaction_list',
    tagName: 'ul',
    classNames: ['reactions']
});

