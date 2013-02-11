
/*
 Models
 */
App.Reaction = DS.Model.extend({
    url: 'reactions',

    text: DS.attr('string'),
    author: DS.belongsTo('App.Member'),
    created: DS.attr('string'),
    timesince: DS.attr('string')
});


App.WallPostReaction = App.Reaction.extend({
    url: 'wallposts/reactions',

    // We need wallpost_id to create reactions in the API
    // This can't be a calculated property because then it won't be part of the API call
    wallpost_id: DS.attr('number'),
    wallpost: DS.belongsTo('App.ProjectWallPost')
});


/*
 Controllers
 */

App.wallPostReactionController = Em.Controller.create({

    addReaction: function(reaction, wallpost) {
        // Do a client side check if Reaction as a reaction property set
        // wallpost.reactions has problems with invalid records an will barf
        if (reaction.get('text') == undefined || reaction.get('text') == "") {
            reaction.set('errors', {'text': ['This field is required']});
            return;
        }

        var transaction = App.store.transaction();
        var newReaction = transaction.createRecord(App.WallPostReaction);
        newReaction.set('text', reaction.get('text'));
        newReaction.set('wallpost_id', wallpost.get('id'));
        // Set the wallpost so the list gets updated in the view
        newReaction.set('wallpost', wallpost);
        newReaction.on('didCreate', function(record) {
            // Clear the reaction text in the form.
            reaction.set('errors', null);
            reaction.set('text', '');
        });
        transaction.commit();

    }
});


/*
 Views
 */

App.WallPostReactionFormView = Em.View.extend({
    templateName: 'reaction_form',
    templateFile: 'reactions',
    tagName: 'form',
    classNames: ['reaction-form'],

    // Each reaction form view needs to have its own reaction model.
    init: function(){
        this._super();
        this.set('content', App.WallPostReaction.createRecord());
    },

    submit: function(e) {
        e.preventDefault();
        App.wallPostReactionController.addReaction(this.get('content'), this.get('parentView.content'));
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


App.ReactionView = Em.View.extend({
    templateName: 'reaction',
    templateFile: 'reactions',
    tagName: 'li',
    classNames: ['initiator'],

    isAuthor: function(){
        var username = this.get('user.username');
        var authorname = this.get('content.author.username');
        if (username) {
            return (username == authorname);
        }
        return false;
    }.property('user', 'content'),

    deleteReaction: function() {
        if (confirm("Delete this reaction?")) {
            var transaction = App.store.transaction();
            var reaction = this.get('content');
            transaction.add(reaction);
            this.$().fadeOut(500, function(){
                reaction.deleteRecord();
                transaction.commit();
            });
        }
    }
});


App.ReactionNoItemsView = Em.View.extend({
    templateName: 'reaction_no_items'
});


App.WallPostReactionListView = Em.CollectionView.extend({
    tagName: 'ul',
    classNames: ['reactions'],
    contentBinding: 'parentView.content.reactions',
    emptyViewClass: 'App.ReactionNoItemsView',
    itemViewClass: 'App.ReactionView'
});

