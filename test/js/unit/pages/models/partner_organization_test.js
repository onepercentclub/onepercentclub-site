pavlov.specify("Partner Organization model unit tests", function(){

    describe("Partner Organization Model", function () {
        it("is a DS.Model", function() {
            assert(App.PartnerOrganization).isDefined();
            assert(DS.Model.detect(App.PartnerOrganization)).isTrue();
        });
    });

    describe("Partner Organization Instance", function () {
        
        before(function() {      
            Ember.run( function () {
                App.injectTestHelpers();
            });
        });

        after(function () {
            Ember.run( function () {
                App.removeTestHelpers();

                App.PartnerOrganization.FIXTURES = [];
            });
        });

        it("should be a new partner organization", function () {
            build('partnerOrganization').then(function(partnerOrganization) {
                assert(partnerOrganization instanceof App.PartnerOrganization).isTrue();
                assert(partnerOrganization.get('isNew')).isTrue();
            });
        });

        it("should have some properties", function () {
            build('partnerOrganization').then(function(partnerOrganization) {
                assert(partnerOrganization.url).equals('partners');
                assert(partnerOrganization.get('name')).equals('Explore The Galaxy');
                assert(partnerOrganization.get('description')).equals('Explore the galaxy and discover new worlds');
                assert(partnerOrganization.get('projects')).isDSArray();
            });
        });

    });

});