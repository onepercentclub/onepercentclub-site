var get = Ember.get, set = Ember.set;

DS.DRF2Serializer = DS.Serializer.extend({

    init: function() {
        this._super();
        this.transforms['array'] = {
            fromJSON: function(serialized) {
                return Ember.none(serialized) ? null : eval(serialized);
            },
            toJSON: function(deserialized) {
                return Ember.none(deserialized) ? null : deserialized.toJSON();
            }
        }
    }
});


DS.DRF2Adapter = DS.RESTAdapter.extend({

    /*
     Use a custom serializer for DRF2.
     */
    serializer: DS.DRF2Serializer,

    /*
     Bulk commits are not supported by this adapter.
     */
    bulkCommit: false,

    /*
     DRF2 uses the 'next' keyword for paginating results.
     */
    since: 'next',

    /*
     Changes from default:
     - don't call sideload() because DRF2 doesn't support it.
     - get results from json.results.
     */
    didFindAll: function(store, type, json) {
        var since = this.extractSince(json);

        store.loadMany(type, json['results']);

        // this registers the id with the store, so it will be passed
        // into the next call to `findAll`
        if (since) {
            store.sinceForType(type, since);
        }

        store.didUpdateAll(type);
    },

    /*
     Changes from default:
     - don't call sideload() because DRF2 doesn't support it.
     - get result from json directly.
     */
    didFindRecord: function(store, type, json, id) {
        store.load(type, id, json);
    },

    /*
     Changes from default:
     - don't call sideload() because DRF2 doesn't support it.
     - get results from json.results.
     */
    didFindQuery: function(store, type, json, recordArray) {
        recordArray.load(json['results']);
    },

    /*
     Changes from default:
     - don't replace CamelCase with '_'.
     - also check for 'url' defined in the class.
     */
    rootForType: function(type) {
        if (type.url) {
            return type.url;
        }
        if (type.proto().url) {
            return type.proto().url;
        }
        // use the last part of the name as the URL
        var parts = type.toString().split(".");
        var name = parts[parts.length - 1];
        return name.toLowerCase();
    },

    /*
     Changes from default:
     - don't add 's' if the url name already ends with 's'.
     */
    pluralize: function(name) {
        if (this.plurals[name])
            return this.plurals[name];
        else if (name.substr(name.length - 1) === 's')
            return name;
        else
            return name + 's';
    }

});
