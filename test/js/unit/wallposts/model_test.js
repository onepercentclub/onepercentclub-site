pavlov.specify("Wallpost model unit tests", function(){

    describe("Wallpost Model", function () {
        it("is a DS.Model", function() {
            assert(App.WallPost).isDefined();
            assert(DS.Model.detect(App.WallPost)).isTrue();
        });
    });

    describe("Wallpost instance", function () {
        
        var wallpost;

        before(function(){
            Ember.run(function() {
                wallpost = App.WallPost.find(9120);
            });
        });

        after(function() {
            Ember.run(function() {
                App.reset();
            });
        });

        it("should have some properties", function () {
            assert(wallpost.url).equals('wallposts');
            assert(wallpost.get('title')).equals(null);
            assert(wallpost.get('text')).equals(null);
            assert(wallpost.get('author')).equals(null);
            assert(wallpost.get('type')).equals(null);
            assert(wallpost.get('created')).equals(null);
            assert(wallpost.get('reactions')).isDSArray();
            assert(wallpost.get('video_url')).equals(null);
            assert(wallpost.get('video_html')).equals(null);
            assert(wallpost.get('photos')).isDSArray();
        });

    });

});