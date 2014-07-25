App.PartnerController = Em.ObjectController.extend({});


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
        removeComma = answer.split(','[0]);
        newAnswer = removeComma[0].replace('.', '');
        
        return (newAnswer <= 15000);
    }.property('questionTwo'),

    actions: {
        answer: function(question, value){
            this.set(question, value);
        }
    }
});
