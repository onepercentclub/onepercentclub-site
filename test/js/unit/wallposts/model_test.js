pavlov.specify("Wallpost model unit tests", function(){

    describe("Wallpost Model", function () {
        it("is a DS.Model", function() {
            assert(App.Wallpost).isDefined();
            assert(DS.Model.detect(App.Wallpost)).isTrue();
        });
    });

    describe("Wallpost instance", function () {

        before(function() {      
            Ember.run( function () {
                App.injectTestHelpers();
            });
        });

        after(function () {
            Ember.run( function () {
                App.removeTestHelpers();

                App.Wallpost.FIXTURES = [];
            });
        });

        it("should be a new wallpost", function () {
            build('wallpost').then(function(wallpost) {
                assert(wallpost instanceof App.Wallpost).isTrue();
                assert(wallpost.get('isNew')).isTrue();
            });
        });

        it('should have some properties', function () {
            build('wallpost').then(function(wallpost) {
                assert(wallpost.url).equals('wallposts');
                assert(wallpost.get('title')).equals('Kick start on the road to clean drinking water');
                assert(wallpost.get('type')).equals('media');
            });
        });

        it('should set isSystemWallpost correctly', function () {
            build('wallpost').then(function(wallpost) {
                assert(wallpost.get('isSystemWallpost')).isFalse();

                wallpost.set('type', 'system');
                return wallpost;
            }).then( function (wallpost) {
                assert(wallpost.get('isSystemWallpost')).isTrue();
            });
        });

    });

});