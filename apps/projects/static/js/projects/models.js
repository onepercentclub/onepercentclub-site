App.Project.reopen({

    amount_asked: DS.attr('number'),
    amount_donated: DS.attr('number'),
    amount_needed: DS.attr('number'),

    task_count: DS.attr('number'),

    isFundable: Em.computed.equal('status.id', '6'),

    isStatusPlan: Em.computed.equal('status.id', '5'),
    isStatusCampaign: Em.computed.equal('status.id', '6'),
    isStatusCompleted: Em.computed.equal('status.id', '8')

});

App.ProjectPreview.reopen({
    url: 'projects/previews'
})

App.MyProject.reopen({
    image: DS.attr('image'),
    video: DS.attr('string'),

    requiredStoryFields: ['description', 'goal', 'destination_impact'],
    requiredPitchFields: ['title', 'pitch', 'image', 'theme', 'tags.length', 'deadline', 'country', 'latitude', 'longitude'],

    friendlyFieldNames: {
        'title' : 'Title',
        'pitch': 'Description',
        'image' : 'Image',
        'theme' : 'Theme',
        'tags.length': 'Tags',
        'deadline' : 'Deadline',
        'country' : 'Country',
        'description': 'Why, what and how',
        'goal' : 'Goal',
        'destination_impact' : 'Destination impact'
    }

});