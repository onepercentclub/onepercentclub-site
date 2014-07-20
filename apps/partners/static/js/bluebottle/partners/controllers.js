App.PartnerController = Em.ObjectController.extend({});


App.CheetahQuizController = Em.Controller.extend({

    questionOne: null,
    questionTwo: null,
    questionThree: null,

    questionOnePassed: Em.computed.equal('questionOne', 'yes'),
    questionOneFailed: Em.computed.equal('questionOne', 'no'),

    questionTwoPassed: function(){
        var answer = this.get('questionTwo');
        if (!answer) return false;
        return (answer <= 10000);
    }.property('questionTwo'),
    questionTwoFailed: Em.computed.gt('questionTwo', 10000),

    questionThreePassed: Em.computed.equal('questionThree', 'yes'),
    questionThreeFailed: Em.computed.equal('questionThree', 'no'),

    actions: {
        answer: function(question, value){
            this.set(question, value);
        }

    }

});
