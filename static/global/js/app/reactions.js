App.Reaction = DS.Model.extend({
    url: 'reactions',
    reaction: DS.attr('string'),
    author: DS.belongsTo('App.Member', {embedded: true}),
    created: DS.attr('string'),
    timesince: DS.attr('string')
});


App.WallPostReaction = DS.Model.extend({
    url: 'wallposts/reactions',
    wallpost_id: DS.attr('number'),
    reaction: DS.attr('string'),
    author: DS.belongsTo('App.Member', {embedded: true}),
    created: DS.attr('string'),
    timesince: DS.attr('string')
});

App.reactionListController = App.ListController.create({
    model: App.Reaction,
    addReaction: function(type, reaction){
        var transaction = App.store.transaction()
        var r = transaction.createRecord(type, reaction);
        transaction.commit();
        return r;
    }
});

App.wallPostReactionController = Em.Controller.create({
    model: App.WallPostReaction,
    loadReaction: function(){
        this.get('wallpost').get('reactions').pushObject(this.get('livereaction'));
    }.observes('livereaction.isLoaded'),
    addReaction: function(reaction, wallpost){
        this.wallpost = wallpost;
        var transaction = App.store.transaction();
        this.livereaction = transaction.createRecord(this.get('model'), reaction.toJSON());
        this.livereaction.set('wallpost_id', wallpost.get('id'));
        transaction.commit();
    }
});


App.ReactionBoxView = Em.View.extend({
    templateName: 'reaction_box',
    templateFile: 'reaction_box',
    classNames: ['container']
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
            $(this).closest('.reaction-form').addClass('is-selected');
        });
        this.$().blur(function(e) {
            $(this).closest('.reaction-form').removeClass('is-selected');
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


App.ReactionListView = Em.CollectionView.extend({
    tagName: 'ul',
    classNames: ['reactions'],
    contentBinding: 'App.reactionListController.content',
    emptyViewClass: 'App.ReactionNoItemsView',
    itemViewClass: 'App.ReactionView'
});

