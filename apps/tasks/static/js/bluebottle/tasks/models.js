/**
 * Embedded mappings
 */

App.Adapter.map('App.Task', {
    author: {embedded: 'load'},
    tags: {embedded: 'always'},
    members: {embedded: 'load'},
    files: {embedded: 'load'}
});
App.Adapter.map('App.TaskPreview', {
    author: {embedded: 'load'},
    project: {embedded: 'load'}
});
App.Adapter.map('App.TaskMember', {
    member: {embedded: 'load'}
});
App.Adapter.map('App.TaskFile', {
    author: {embedded: 'load'}
});


/*
 Models
 */

App.TaskMember = DS.Model.extend({
    url: 'tasks/members',

    member: DS.belongsTo('App.UserPreview'),
    created: DS.attr('date'),
    status: DS.attr('string', {defaultValue: 'applied'}),
    motivation: DS.attr('string'),
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
    skill: DS.belongsTo('App.Skill'),

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


App.Skill = DS.Model.extend({
    url: 'tasks/skills',
    name: DS.attr('string')
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
    skill: DS.attr('string'),
    ordering: DS.attr('string', {defaultValue: 'newest'}),
    status: DS.attr('string', {defaultValue: 'open'}),
    page: DS.attr('number', {defaultValue: 1})

});
