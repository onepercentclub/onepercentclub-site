pavlov.specify("Page model unit tests", function(){

    describe("Page Model", function () {
        it("is a DS.Model", function() {
            assert(App.Page).isDefined();
            assert(DS.Model.detect(App.Page)).isTrue();
        });
    });

    describe("Page Instance", function () {
        
        var page;

        before(function(){
            Ember.run(function() {
                page = App.Page.createRecord({title: 'A Title', body: 'A Body'});
            });
        });

        after(function() {
            Ember.run(function() {
                App.reset();
            });
        });

        it("is a DS.Model", function() {
            assert(App.Page).isDefined();
            assert(DS.Model.detect(App.Page)).isTrue();
        });

        it("should have some properties", function () {
            assert(page.get('title')).equals('A Title');
            assert(page.get('body')).equals('A Body');
        });

    });

});