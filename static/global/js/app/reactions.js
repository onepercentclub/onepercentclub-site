App.Reaction = DS.Model.extend({
    url: 'reactions',

    reaction: DS.attr('string'),
    author: DS.belongsTo('App.Member', {embedded: true}),
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


App.wallPostReactionController = Em.Controller.create({
    model: App.WallPostReaction,

    addReaction: function(reaction, wallpost) {
        // Do a client side check if Reaction as a reaction property set
        // wallpost.reactions has problems with invalid records an will barf
        if (reaction.get('reaction') == undefined || reaction.get('reaction') == "") {
            reaction.set('errors', {'reaction': ['This field is required']});
            return false;
        }
        var transaction = App.store.transaction();
        var model = this.get('model');
        var livereaction = transaction.createRecord(model, reaction.toJSON());
        // Set the wallpost so the list gets updated in the view
        livereaction.set('wallpost_id', wallpost.get('id'));
        livereaction.set('wallpost', wallpost);
        livereaction.on('didCreate', function(record) {
            // Clear the reaction text in the form
            reaction.set('errors', null);
            reaction.set('reaction', '');
        });
        transaction.commit();
    }
});


App.WallPostReactionFormView = Em.View.extend({
    templateName: 'reaction_form',
    templateFile: 'reactions',
    tagName: 'form',
    classNames: ['reaction-form'],

    wallpostBinding: "parentView.content",

    content: App.wallPostReactionController.get('model').createRecord(),

    submit: function(e) {
        e.preventDefault();
        App.wallPostReactionController.addReaction(this.get('content'), this.get('wallpost'));
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

    deleteReaction: function(e) {
        if (confirm("Delete this reaction?")) {
            e.preventDefault();
            var transaction = App.store.transaction();
            var reaction = this.get('content');
            transaction.add(reaction);
            // Clear author here
            // TODO: Have a proper solution for belongsTo fields in adapter
            reaction.reopen({
                author: null
            });
            this.$().fadeOut(500, function(){
                reaction.deleteRecord();
                transaction.commit();
            });
        }
    }});


App.ReactionNoItemsView = Em.View.extend({
    templateName: 'reaction_no_items',
    templateFile: 'reactions'
});


App.WallPostReactionListView = Em.CollectionView.extend({
    tagName: 'ul',
    classNames: ['reactions'],
    contentBinding: 'parentView.content.reactions',
    emptyViewClass: 'App.ReactionNoItemsView',
    itemViewClass: 'App.ReactionView'
});

