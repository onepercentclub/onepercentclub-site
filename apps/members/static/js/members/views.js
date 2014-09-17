
App.TimeAvailableSelect = Em.Select.extend({
    prompt: gettext('Pick a time slot'),
    name: 'timeavailable'
});

App.Why = Em.TextArea.extend({
	placeholder: gettext("Tell the world why you chose to join 1%Club!")
});

App.AboutYou = Em.TextArea.extend({
	placeholder: gettext("Tell us a bit about yourself so we can get to know you!")
});

App.FirstName = Em.TextArea.extend({
	placeholder: gettext("First name")
});

App.Surname = Em.TextArea.extend({
	placeholder: gettext("Surname") 
});