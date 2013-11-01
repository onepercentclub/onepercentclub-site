Factory.define('task', { 
    author: function() {
    	return attr('userPreview');
    },
    title: 'Takeover Naboo',
    description: 'Title says it all',
    end_goal: 'Description says it all',
    status: 'open'
});