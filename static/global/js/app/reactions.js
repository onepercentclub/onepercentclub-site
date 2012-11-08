App.Reaction = DS.Model.extend({
    url: 'reactions',
    reaction: DS.attr('string'),
});


App.reactionListController = App.ListController.create({
    model: App.Reaction,
    getList: function(filterParams){
        var slug = filterParams['slug'];
        var type = filterParams['type'];
        var url =  type + '/' + slug + '/reactions';
        var model =  this.get('model');
        model.reopen({
            url: url
        });
        this.set("content", App.store.findAll(model));
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
    classNames: ['reaction-form']
});


App.ReactionPreviewView = Em.View.extend({
    templateName: 'reaction_preview',
    templateFile: 'reaction_list'
    
});

App.ReactionNoItemsView = Em.View.extend({
    templateName: 'reaction_no_items',
    templateFile: 'reaction_list',
});


App.ReactionListView = Em.CollectionView.extend({
    tagName: 'ul',
    classNames: ['reactions'],
    contentBinding: 'App.reactionListController.content',
    emptyViewClass: 'App.ReactionNoItemsView',
    itemViewClass: 'App.ReactionPreviewView',
});

