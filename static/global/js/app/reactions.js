
/*
 Models
 */

App.WallPostReaction = DS.Model.extend({
    url: 'wallposts/reactions',

    text: DS.attr('string'),
    author: DS.belongsTo('App.Member'),
    created: DS.attr('string'),
    timesince: DS.attr('string'),
    wallpost: DS.belongsTo('App.ProjectWallPost')
});


/*
 Controllers
 */

App.WallPostReactionController = Em.ObjectController.extend(App.IsAuthorMixin, App.DeleteModelMixin, {
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
        var transaction = this.get('store').transaction();
        var reaction =  transaction.createRecord(App.WallPostReaction);
        this.set('model', reaction);
        this.set('transaction', transaction);
    },

    addReaction: function() {
        var reaction = this.get('model');
        // Set the wallpost that this reaction is related to.
        reaction.set('wallpost', this.get('currentWallpost'));

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
            var controller = this.get('controller');
            this.$().fadeOut(500, function() {
                controller.deleteRecordOnServer()
            });
        }
    }
});


App.WallPostReactionListView = Em.View.extend({
    templateName: 'wallpost_reaction_list',
    tagName: 'ul',
    classNames: ['reactions']
});

