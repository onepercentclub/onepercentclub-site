App.CheetahQuizController = Em.Controller.extend({
    questionOne: null,
    questionTwo: null,
    questionThree: null,

    questionOnePassed: Em.computed.equal('questionOne', 'yes'),
    questionOneFailed: Em.computed.equal('questionOne', 'no'),
    questionTwoFailed: Em.computed.gt('questionTwo', 15000),
    questionThreePassed: Em.computed.equal('questionThree', 'yes'),
    questionThreeFailed: Em.computed.equal('questionThree', 'no'),

    questionTwoPassed: function(){
        var answer = this.get('questionTwo'),
            removeComma, newAnswer;

        if (!answer) return false;
        return (answer <= 15000);
    }.property('questionTwo'),

    actions: {
        answer: function(question, value){
            this.set(question, value);
        }
    }
});

App.PartnerController = Em.ObjectController.extend({
    project: null,

    favouriteProjects: function () {
        return this.get('projects').slice(0, 3);
    }.property('projects.length'),

    actions: {
        goToFavouriteProject: function(project) {
            if (this.get('tracker')) {
                this.get('tracker').trackEvent("Click Favourite Project", {title: project.get("title")});
            }
            this.transitionToRoute('project', project);
        }
    }
});