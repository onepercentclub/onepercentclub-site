Factory.define('task', { 
    author: function() {
    	return attr('userPreview');
    },
    title: 'Takeover Naboo',
    description: 'Title says it all',
    end_goal: 'Description says it all',
    status: 'open',
    time_needed: 8
});

Factory.define('taskFile', {
	author: function () {
		return attr('user');
	},
    task: function () {
    	return attr('task');
    },
	title: 'Death Star Blueprints',
    file: 'deathstar.pdf'
});

Factory.define('skill', {
	name: 'Engineer'
});

Factory.define('taskMember', {
	member: function () {
		return attr('userPreview');
	},
	task: function () {
    	return attr('task');
    },
	status: 'applied',
	motivation: 'Build a better Death Star',
});

Factory.define('taskSearch', {
	text: 'star',
	skill: 'Engineer',
	ordering: 'newest',
	status: 'open',
	page: 1
});