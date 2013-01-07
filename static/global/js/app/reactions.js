App.Reaction = DS.Model.extend({
    url: 'reactions',
    reaction: DS.attr('string'),
    author: DS.belongsTo('App.Member'),
    created: DS.attr('string'),
    relativetime: function(){
        var date = new Date(this.get('created'));
        return date;
        return humanize.relativeTime(date.getTime());
    }.property('created')
});


App.reactionListController = App.ListController.create({
    model: App.Reaction,
    getUrl: function(){
        
    },
    getList: function(filterParams){
        var slug = filterParams['slug'];
        var type = filterParams['type'];
        var url =  type + '/' + slug + '/reactions/';
        var model =  this.get('model');
        model.reopen({
            'url': url
        });
        this.set("content", App.store.findAll(model));
    },
    addReaction: function(reaction){
        App.Reaction.createRecord({'reaction': reaction});
        App.store.commit();
    }
});

App.reactionBoxController = Em.Controller.create({
});


App.ReactionBoxView = Em.View.extend({
    templateName: 'reaction_box',
    templateFile: 'reaction_box',
    classNames: ['container']
});


App.ReactionFormView = Em.View.extend({
    templateName: 'reaction_form',
    templateFile: 'reaction_box',
    tagName: 'form',
    classNames: ['reaction-form'],
    reaction: '',
    submit: function(e){
        e.preventDefault();
        App.reactionListController.addReaction(this.get('reaction'));
    }
});


App.ReactionPreviewView = Em.View.extend({
    templateName: 'reaction_preview',
    templateFile: 'reaction_list'
    
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
    itemViewClass: 'App.ReactionPreviewView'
});

