App.Task.reopen({
    isAvailable: function () {
        var now = new Date();
        return (this.get('isStatusOpen') || this.get('isStatusInProgress')) && this.get('people_needed') > this.get('membersCount') && this.get('deadline') > now;
    }.property('isStatusOpen', 'isStatusInProgress', 'people_needed', 'membersCount', 'deadline'),
});
