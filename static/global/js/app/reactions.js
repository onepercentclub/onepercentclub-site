App.Reaction = DS.Model.extend({
    url: 'reactions',
    reaction: DS.attr('string'),
    author: DS.belongsTo('App.Member', {embedded: true}),
    created: DS.attr('string'),
    timesince: DS.attr('string')
});


App.WallPostReaction = DS.Model.extend({
    url: 'wallposts/reactions',
    // We need wallpost_id to create reactions in the API
    // This can't be a calculated property because then it won't be part of the API call
    wallpost_id: DS.attr('number'),
    wallpost: DS.belongsTo('App.ProjectWallPost'),
    reaction: DS.attr('string'),
    author: DS.belongsTo('App.Member', {embedded: true}),
    created: DS.attr('string'),
    timesince: DS.attr('string')
});

App.wallPostReactionController = Em.Controller.create({
    model: App.WallPostReaction,
    addReaction: function(reaction, wallpost){
        var transaction = App.store.transaction();
        var model = this.get('model');
        var livereaction = transaction.createRecord(model, reaction.toJSON());
        // Set the wallpost so the list gets updated in the view
        livereaction.set('wallpost_id', wallpost.get('id'));
        livereaction.set('wallpost', wallpost);
        livereaction.on('didCreate', function(record){
            // Clear the reaction text in the form
            reaction.set('reaction', '');
        });
        transaction.commit();
    }
});


App.WallPostReactionFormView = Em.View.extend({
    templateName: 'reaction_form',
    templateFile: 'reaction_box',
    tagName: 'form',
    classNames: ['reaction-form'],
    wallpostBinding: "parentView.content",
    modelBinding: "App.wallPostReactionController.model",
    reaction: function(){
        return this.get('model').createRecord();
    }.property('model'),
    submit: function(e){
        e.preventDefault();
        App.wallPostReactionController.addReaction(this.get('reaction'), this.get('wallpost'));

    },
    didInsertElement: function(e){
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
    templateFile: 'reaction_list',
    tagName: 'li',
    classNames: ['initiator']
});


App.ReactionNoItemsView = Em.View.extend({
    templateName: 'reaction_no_items',
    templateFile: 'reaction_list'
});


App.ReactionActionsView = Em.View.extend({
    countBinding: 'App.reactionListController.count',
    templateName: 'reaction_actions',
    templateFile: 'reaction_box'
});


App.WallPostReactionListView = Em.CollectionView.extend({
    tagName: 'ul',
    classNames: ['reactions'],
    contentBinding: 'parentView.content.reactions',
    emptyViewClass: 'App.ReactionNoItemsView',
    itemViewClass: 'App.ReactionView'
});

