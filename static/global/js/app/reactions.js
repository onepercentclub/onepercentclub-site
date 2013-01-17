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
    addReaction: function(reaction, wallpost){
        var transaction = App.store.transaction();
        var livereaction = transaction.createRecord(this.get('model'), reaction.toJSON());
        livereaction.set('wallpost_id', wallpost.get('id'));
        livereaction.on('didCreate', function(record, a, b){
            console.log(a);
            console.log(b);
            console.log(record);
            wallpost.get('reactions').pushObject(record);
        });
        alert('wait');
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
        this.get('reaction').on('becameError', function(){
            this.set('reaction', reaction);
        });
        this.get('reaction').on('didLoad', function(){
            this.set('reaction', this.get('model').createRecord());
        });

    },
    didInsertElement: function(e){
        this.$('textarea').focus(function(e) {
            $(this).parents('.reaction-form').addClass('is-selected');
        });
        this.$().blur(function(e) {
            $(this).parents('.reaction-form').removeClass('is-selected');
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

