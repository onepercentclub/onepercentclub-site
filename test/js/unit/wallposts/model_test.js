pavlov.specify("Wallpost model unit tests", function(){

    describe("Wallpost Model", function () {
        it("is a DS.Model", function() {
            assert(App.WallPost).isDefined();
            assert(DS.Model.detect(App.WallPost)).isTrue();
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

                App.WallPost.FIXTURES = [];
            });
        });

        it("should be a new wallpost", function () {
            build('wallPost').then(function(wallPost) {
                assert(wallPost instanceof App.WallPost).isTrue();
                assert(wallPost.get('isNew')).isTrue();
            });
        });

        it('should have some properties', function () {
            build('wallPost').then(function(wallPost) {
                assert(wallPost.url).equals('wallposts');
                assert(wallPost.get('title')).equals('Kick start on the road to clean drinking water');
                assert(wallPost.get('type')).equals('media');
            });
        });

        it('should set isSystemWallPost correctly', function () {
            build('wallPost').then(function(wallPost) {
                assert(wallPost.get('isSystemWallPost')).isFalse();

                wallPost.set('type', 'system');
                return wallPost;
            }).then( function (wallPost) {
                assert(wallPost.get('isSystemWallPost')).isTrue();
            });
        });

    });

});