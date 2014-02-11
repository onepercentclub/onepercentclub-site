App.Project.reopen({

    isStatusPlan: Em.computed.equal('status.id', 5),
    isStatusCampaign: Em.computed.equal('status.id', 6),
    isStatusCompleted: Em.computed.equal('status.id', 8)

});