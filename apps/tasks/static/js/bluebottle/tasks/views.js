
/*
 Views
 */

App.TaskListView = Em.View.extend({
    templateName: 'task_list'
});

App.TaskPreviewView = Em.View.extend({
    templateName: 'task_preview'
});


App.ProjectTaskListView = Em.View.extend(App.ScrollInView, {});


App.ProjectTaskView = Em.View.extend(App.ScrollInView, {
    templateName: 'task'
});


App.TaskMenuView = Em.View.extend({
    templateName: 'task_menu',
    tagName: 'form'
});



App.ProjectTaskNewView = Em.View.extend(App.ScrollInView, {
    templateName: 'task_new',

    submit: function(e) {
        e.preventDefault();
        this.get('controller').createTask();
    }
});


App.ProjectTaskEditView = Em.View.extend(App.ScrollInView, {
    templateName: 'task_edit',

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

App.TaskMemberApplyView = Em.View.extend({
    templateName: 'task_member_apply',
    tagName: 'form',
    motivation: ''
});


App.TaskFileNewView = Em.View.extend({
    templateName: 'task_file_new',
    tagName: 'form',

    addFile: function(e) {
        e.preventDefault();
        this.get('controller').uploadTaskFile();
    }
});


App.TaskDeadLineDatePicker = App.DatePicker.extend({
    config: {minDate: 0, maxDate: "+3M"}
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


App.SkillSelectView = Em.Select.extend({
    optionValuePath: "content",
    optionLabelPath: "content.name",
    prompt: "Pick a skill"
});
