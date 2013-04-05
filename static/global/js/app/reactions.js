
/*
 Models
 */

App.WallPostReaction = DS.Model.extend({
    url: 'wallposts/reactions',

    text: DS.attr('string'),
    author: DS.belongsTo('App.Member'),
    created: DS.attr('date'),
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
            $(this).closest('.reaction-form').addClass('is-selected');
        }).blur(function(e) {
            if (!$.trim($(this).val())) {
                // textarea is empty or contains only white-space
                $(this).closest('.reaction-form').removeClass('is-selected');
            }
        });
    }
});


App.WallPostReactionView = Em.View.extend({
    templateName: 'wallpost_reaction',
    tagName: 'li',
    classNames: ['initiator'],

    deleteReaction: function() {
        var view = this;
        bootbox.confirm('Are you sure you want to delete this reaction?', function(value){
            if (value) {
                view.$().fadeOut(500, function() {
                    view.get('controller').deleteRecordOnServer()
                });
            }
        });
    }
});


App.WallPostReactionListView = Em.View.extend({
    templateName: 'wallpost_reaction_list',
    tagName: 'ul',
    classNames: ['reactions']
});

