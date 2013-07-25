(function() {

    var get = Ember.get, set = Ember.set;

    Ember.Location.registerImplementation('hashbang', Ember.HashLocation.extend({

        getURL: function() {
            return get(this, 'location').hash.substr(2);
        },

        setURL: function(path) {
            get(this, 'location').hash = "!" + path;
            set(this, 'lastSetURL', "!" + path);
        },

        onUpdateURL: function(callback) {
            var self = this;
            var guid = Ember.guidFor(this);

            Ember.$(window).bind('hashchange.ember-location-' + guid, function() {
            Ember.run(function() {
                var path = location.hash.substr(1);
                if (get(self, 'lastSetURL') === path) { return; }

                set(self, 'lastSetURL', null);

                callback(location.hash.substr(2));
            });
            });
        },

        formatURL: function(url) {
            return '#!' + url;
        }

    }));

})();