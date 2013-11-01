pavlov.specify("Contact Message model unit tests", function(){

    describe("Contact Message", function () {
        it("is a DS.Model", function() {
            assert(App.ContactMessage).isDefined();
            assert(DS.Model.detect(App.ContactMessage)).isTrue();
        });
    });

    describe("Contact Message Instance", function () {
        
        before(function() {      
            Ember.run( function () {
                App.injectTestHelpers();
            });
        });

        after(function () {
            Ember.run( function () {
                App.removeTestHelpers();

                App.ContactMessage.FIXTURES = [];
            });
        });

        it("should be a new contact message", function () {
            build('contactMessage').then(function(contactMessage) {
                assert(contactMessage instanceof App.ContactMessage).isTrue();
                assert(contactMessage.get('isNew')).isTrue();
            });
        });

        it("should have some properties", function () {
            build('contactMessage').then(function(contactMessage) {
                assert(contactMessage.url).equals('pages/contact');
                assert(contactMessage.get('name')).equals('Darth Vader');
                assert(contactMessage.get('email')).equals('darth@gmail.com');
            });
        });

        it("should set isComplete correctly", function () {
            build('contactMessage').then(function(contactMessage) {
                assert(contactMessage.get('isComplete')).isTrue();

                contactMessage.set('email', null);
                return contactMessage;
            }).then( function (contactMessage) {
                assert(contactMessage.get('isComplete')).isFalse();                
            });
        });

        it("should set isSent correctly", function () {
            build('contactMessage').then(function(contactMessage) {
                assert(contactMessage.get('id')).isDefined();
                assert(contactMessage.get('isSent')).isTrue();
            });
        });

    });

});