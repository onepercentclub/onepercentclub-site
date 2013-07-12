/*
 Models
 */

App.TaskMember = DS.Model.extend({
    url: 'tasks/members',

    member: DS.belongsTo('App.User'),
    created: DS.attr('date'),
    status: DS.attr('string', {defaultValue: 'applied'}),
    task: DS.belongsTo('App.Task'),
    isStatusApplied: function(){
        return (this.get('status') == 'applied');
    }.property('status'),
    isStatusAccepted: function(){
        return (this.get('status') == 'accepted');
    }.property('status'),
    isStatusRejected: function(){
        return (this.get('status') == 'rejected');
    }.property('status'),
    isStatusRealized: function(){
        return (this.get('status') == 'realized');
    }.property('status')
});

App.TaskFile = DS.Model.extend({
    url: 'tasks/files',

    author: DS.belongsTo('App.User'),
    title: DS.attr('string'),
    created: DS.attr('date'),
    file: DS.attr('file'),
    task: DS.belongsTo('App.Task')
});

App.Task = DS.Model.extend({
    url: 'tasks',

    // Model fields
    author: DS.belongsTo('App.UserPreview'),
    title: DS.attr('string'),
    description: DS.attr('string'),
    end_goal: DS.attr('string'),
    created: DS.attr('date'),
    deadline: DS.attr('date'),
    project: DS.belongsTo('App.Project'),
    members: DS.hasMany('App.TaskMember'),
    files: DS.hasMany('App.TaskFile'),
    expertise: DS.attr('string'),
    location: DS.attr('string', {defaultValue: ''}),
    time_needed: DS.attr('number'),
    status: DS.attr('string', {defaultValue: 'open'}),
    tags: DS.hasMany('App.Tag'),
    wallposts: DS.hasMany('App.WallPost'),

    // Calculate status booleans here so we can use it in all views
    isStatusOpen: function(){
        return this.get('status') == 'open';
    }.property('status'),

    isStatusInProgress: function(){
        return this.get('status') == 'in progress';
    }.property('status'),

    isStatusClosed: function(){
        return this.get('status') == 'closed';
    }.property('status'),

    isStatusRealized: function(){
        return this.get('status') == 'realized';
    }.property('status'),

    timeNeeded: function(){
        var times = App.TimeNeededList;
        var hours = this.get('time_needed');
        for (time in times) {
            if (times[time].value == hours) {
                return times[time].title;
            }
        }
        return hours + ' hours';
    }.property('time_needed')

});

App.NewTask = App.Task.extend({
    project: DS.belongsTo('App.Project')
});


/*
Preview model that doesn't contain all the properties.
 */
App.TaskPreview = App.Task.extend({
    url: 'tasks/previews',
    project: DS.belongsTo('App.ProjectPreview')
});


App.TaskSearch = DS.Model.extend({

    text: DS.attr('string'),
    skill:  DS.attr('string'),
    ordering: DS.attr('string', {defaultValue: 'newest'}),
    status: DS.attr('string', {defaultValue: 'open'}),
    page: DS.attr('number', {defaultValue: 1})

});


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
                'expertise': this.get('skill')
            };
            var tasks = App.TaskPreview.find(query);
            list.set('model', tasks);
        }
    }.observes('text', 'skill', 'status', 'page', 'ordering')


});


App.ProjectTaskListController = Em.ArrayController.extend({
    needs: ['currentUser', 'project'],
    isProjectOwner: function() {
        var username = this.get('controllers.currentUser.username');
        var ownername = this.get('controllers.project.model.owner.username');
        if (username) {
            return (username == ownername);
        }
        return false;
    }.property('controllers.project.model.owner', 'controllers.currentUser.username')
});


App.ProjectTaskController = Em.ObjectController.extend({
    needs: ['currentUser', 'project'],


    isAuthor: function() {
        var username = this.get('controllers.currentUser.username');
        var author_name = this.get('author.username');
        if (username) {
            return (username == author_name);
        }
        return false;
    }.property('author.username', 'controllers.currentUser.username'),

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
    needs: ['project', 'currentUser', 'projectTaskList'],
    addTask: function(event){
        var controller = this;
        var task = this.get('content');
        task.set('project', this.get('controllers.project.model'));
        task.on('didCreate', function(record) {
            controller.transitionToRoute('projectTaskList')
        });
        task.on('becameInvalid', function(record) {
            controller.set('errors', record.get('errors'));
        });
        task.transaction.commit();
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
            controller.get('controllers.projectTaskList').unshiftObject(record);
            controller.transitionToRoute('projectTask', task);
        });
        task.on('becameInvalid', function(record) {
            controller.set('errors', record.get('errors'));
        });
        task.transaction.commit();
    },
    cancelChangesToTask: function(event){
        var task = this.get('content');
        task.transaction.rollback();
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


/*
 Views
 */

App.TaskListView = Em.View.extend({
    templateName: 'task_list'
});

App.TaskPreviewView = Em.View.extend({
    templateName: 'task_preview'
});


App.ProjectTaskListView = Em.View.extend({
    templateName: 'project_task_list'
});


App.ProjectTaskView = Em.View.extend({
    templateName: 'task'
});


App.TaskMenuView = Em.View.extend({
    templateName: 'task_menu',
    tagName: 'form'
});



App.ProjectTaskNewView = Em.View.extend({
    templateName: 'task_new',
    tagName: 'form',

    submit: function(e) {
        e.preventDefault();
        this.get('controller').addTask();
    }
});


App.ProjectTaskEditView = Em.View.extend({
    templateName: 'task_edit',
    tagName: 'form',

    submit: function(e) {
        e.preventDefault();
        this.get('controller').updateTask();
    }
});


App.TaskMemberEdit = Em.View.extend({
    templateName: 'task_member_edit',
    tagName: 'form',

    submit: function(e) {
        e.preventDefault();
        this.get('controller').updateTaskMember();
    }
});


App.TaskFileNewView = Em.View.extend({
    templateName: 'task_file_new',
    tagName: 'form',

    addFile: function(e) {
        e.preventDefault();
        this.get('controller').uploadTaskFile();
    }
});


App.TaskDeadLineDatePickerView = Ember.TextField.extend({
    classNames: ['ember-text-field', 'input-small'],


    didInsertElement: function(){
        // TODO: fix date formatting, make this prop a 'date' on Task model
        // Idea: Render a hidden field to hold the actual date and a text field to
        // show it in the localized style.
        // Remove dateFormat here will result in locale aware date.
        this.$().datepicker({minDate: 0, maxDate: "+3M", dateFormat: 'yy-mm-dd'});
    },
    change: function(){
        // TODO: This gets a date object,,,
        //this.set('value', this.$().datepicker('getDate'));

    }
});


/*
 Form Elements
 */

App.TaskStatusList = [
    {value: 'open', title: "open"},
    {value: 'in progress', title: "in progress"},
    {value: 'realized', title: "realised"}
];

App.TaskStatusSelectView = Em.Select.extend({
    content: App.TaskStatusList,
    optionValuePath: "content.value",
    optionLabelPath: "content.title",
    prompt: "any status"

});


