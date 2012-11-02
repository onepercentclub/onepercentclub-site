App.blogListController = App.ListController.create({
    init: function() {
        this._super();
        this.getList();
    },
    dataUrl: 'blogs/',
    getList: function(){
        var controller = this;
        require(['app/data_source'], function(){
            App.dataSource.get(controller.getDataUrl(), controller.getFilterParams(), function(data) {
                controller.set('content', data['results']);
            });
        })
    }
});


App.blogDetailController = App.DetailController.create({
    dataUrl: 'blogs/',
});


App.BlogDetailView = Em.View.extend({
    contentBinding: 'App.blogDetailController',
    templateName: 'blog_detail',
    classNames: ['lightgreen', 'section'],
});

App.BlogPreviewView = Em.View.extend({
    templateName: 'blog_preview',
    templateFile: 'blog_list'
    
});

App.BlogNoItemsView = Em.View.extend({
    templateName: 'blog_no_items',
    templateFile: 'blog_list'
    
});


App.BlogListView = Em.CollectionView.extend({
    tagName: 'ul',
    contentBinding: 'App.blogListController',
    emptyViewClass: 'App.BlogNoItemsView',
    itemViewClass: 'App.BlogPreviewView',
});

