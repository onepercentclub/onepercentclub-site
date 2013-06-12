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
    file: DS.attr('string'),
    file_size: DS.attr('string'),
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
    project: DS.belongsTo('App.ProjectPreview'),
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

/*
Preview model that won't contain all the properties.
 */
App.TaskPreview = App.Task.extend({

});



/*
 Controllers
 */


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
    }.property('status'),



});


App.ProjectTaskNewController = Em.ObjectController.extend({
    needs: ['project', 'currentUser', 'projectTaskList'],
    addTask: function(event){
        var controller = this;
        var task = this.get('content');
        task.set('project', this.get('controllers.project.model'));
        task.set('author', this.get('controllers.currentUser.model'));
        task.on('didCreate', function(record) {
            controller.get('controllers.projectTaskList').unshiftObject(record);
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

App.ProjectTaskListView = Em.View.extend({
    templateName: 'task_list'
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



