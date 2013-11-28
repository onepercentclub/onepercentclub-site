/*
 Controllers
 */


App.TaskListController = Em.ArrayController.extend({
    needs: ['taskSearchForm']
});


App.TaskSearchFormController = Em.ObjectController.extend({
    needs: ['taskList'],

    init: function(){
        var form =  App.TaskSearch.createRecord();
        this.set('model', form);
        this.updateSearch();
    },

    rangeStart: function(){
        return this.get('page') * 8 -7;
    }.property('controllers.taskList.model.length'),

    rangeEnd: function(){
        return this.get('page') * 8 -8 + this.get('controllers.taskList.model.length');
    }.property('controllers.taskList.model.length'),

    hasNextPage: function(){
        var next = this.get('page') * 8 -7;
        var total = this.get('controllers.taskList.model.meta.total');
        return (next < total);
    }.property('controllers.taskList.model.meta.total'),

    hasPreviousPage: function(){
        return (this.get('page') > 1);
    }.property('page'),

    nextPage: function(){
        this.incrementProperty('page');
    },

    previousPage: function(){
        this.decrementProperty('page');
    },

    sortOrder: function(order) {
        this.set('ordering', order);
    },

    orderedByNewest: function(){
        return (this.get('ordering') == 'newest');
    }.property('ordering'),
    orderedByDeadline: function(){
        return (this.get('ordering') == 'deadline');
    }.property('ordering'),

    clearForm: function(sender, key) {
        this.set('model.text', '');
        this.set('model.skill', null);
        this.set('model.status', null);
    },

    updateSearch: function(sender, key){
        if (key != 'page') {
            // If the query changes we should jump back to page 1
            this.set('page', 1);
        }
        if (this.get('model.isDirty') ) {
            var list = this.get('controllers.taskList');
            var controller = this;

            var query = {
                'page': this.get('page'),
                'ordering': this.get('ordering'),
                'status': this.get('status'),
                'text': this.get('text'),
                'skill': this.get('skill.id')
            };
            var tasks = App.TaskPreview.find(query);
            list.set('model', tasks);
        }
    }.observes('text', 'skill', 'status', 'page', 'ordering')


});


App.IsProjectOwnerMixin = Em.Mixin.create({
    isProjectOwner: function() {
        var username = this.get('controllers.currentUser.username');
        var ownername = this.get('controllers.project.model.owner.username');
        if (username) {
            return (username == ownername);
        }
        return false;
    }.property('controllers.project.model.owner', 'controllers.currentUser.username')
});


App.ProjectTasksIndexController = Em.ArrayController.extend(App.IsProjectOwnerMixin, {
    needs: ['currentUser', 'project']
});


App.ProjectTaskController = Em.ObjectController.extend(App.IsProjectOwnerMixin, App.IsAuthorMixin, {
    needs: ['currentUser', 'project'],

    isMember: function() {
        var user = this.get('controllers.currentUser.username');
        var isMember = false;
        this.get('model.members').forEach(function(member) {
            var mem = member.get('member.username');
            if (mem == user) {
                isMember =  true;
            }
        });
        return isMember;
    }.property('members.@each.member.username', 'controllers.currentUser.username')

});


App.ProjectTaskIndexController = Em.ArrayController.extend({
    needs: ['projectTask', 'currentUser'],
    perPage: 5,
    page: 1,


    remainingItemCount: function(){
        if (this.get('meta.total')) {
            return this.get('meta.total') - (this.get('page')  * this.get('perPage'));
        }
        return 0;
    }.property('page', 'perPage', 'meta.total'),

    canLoadMore: function(){
        var totalPages = Math.ceil(this.get('meta.total') / this.get('perPage'));
        return totalPages > this.get('page');
    }.property('perPage', 'page', 'meta.total'),

    actions: {
        showMore: function() {
            var controller = this;
            var page = this.incrementProperty('page');
            var id = this.get('controllers.projectTask.model.id');
            App.WallPost.find({'parent_type': 'task', 'parent_id': id, page: page}).then(function(items){
                controller.get('model').pushObjects(items.toArray());
            });
        }
    },
    isOwner: function() {
        var username = this.get('controllers.currentUser.username');
        var ownername = this.get('controllers.projectTask.model.owner.username');
        if (username) {
            return (username == ownername);
        }
        return false;
    }.property('controllers.projectTask.model.owner', 'controllers.currentUser.username')

});


App.TaskMemberController = Em.ObjectController.extend({
    isStatusApplied: function(){
        return this.get('status') == 'applied';
    }.property('status'),

    isStatusInProgress: function(){
        return this.get('status') == 'in progress';
    }.property('status'),

    isStatusClosed: function(){
        return this.get('status') == 'closed';
    }.property('status'),

    isStatusRealized: function(){
        return this.get('status') == 'realized';
    }.property('status')
});


App.ProjectTaskNewController = Em.ObjectController.extend({
    needs: ['project', 'currentUser', 'projectTasksIndex'],
    createTask: function(event){
        var controller = this;
        var task = this.get('content');
        task.set('project', this.get('controllers.project.model'));
        task.on('didCreate', function(record) {
            controller.transitionToRoute('projectTasks')
        });
        task.on('becameInvalid', function(record) {
            //controller.set('errors', record.get('errors'));
        });
        task.save();
    }
});


App.ProjectTaskEditController = App.ProjectTaskNewController.extend({
    updateTask: function(event){
        var controller = this;
        var task = this.get('content');
        if (task.get('isDirty') == false){
            controller.transitionToRoute('projectTask', task);
        }
        task.on('didUpdate', function(record) {
            controller.transitionToRoute('projectTasks', task);
        });
        task.on('becameInvalid', function(record) {
            //controller.set('errors', record.get('errors'));
        });
        task.save();
    },
    cancelChangesToTask: function(event){
        var task = this.get('content');
        task.rollback();
        this.transitionToRoute('projectTask', task);
    }

});


App.TaskPreviewController = Em.ObjectController.extend({
});


App.TaskMemberEditController = Em.ObjectController.extend({
});


App.TaskFileNewController = Em.ObjectController.extend({
    addFile: function(file) {
        this.set('model.file', file);
    }
});

