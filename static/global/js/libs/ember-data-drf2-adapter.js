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
     - don't embed record within 'root' in the json.
     */
    createRecord: function(store, type, record) {
        var root = this.rootForType(type);
        var data = this.toJSON(record, { includeId: true });

        this.ajax(this.buildURL(root), "POST", {
            data: data,
            context: this,
            success: function(json) {
                this.didCreateRecord(store, type, record, json);
            },
            // Make sure we parse any errors.
            error: function(xhr) {
                this.didError(store, type, record, xhr);
            }
        });
    },

    /**
     * Add an error text to a record
     */
    didError: function(store, type, record, xhr) {
        // 422 [The request was well-formed but was unable to be followed due to semantic errors] 
        // seems the right API response. 
        // Because DRF2 returns invalid records with 400 code we catch those too.  
        if (xhr.status === 422 || xhr.status == 400) {
            var data = JSON.parse(xhr.responseText);
            store.recordWasInvalid(record, data);
        } else {
            store.recordWasError(record);
        }
    },

    /*
     Changes from default:
     - don't call sideload() because DRF2 doesn't support it.
     - get result from json directly.
     */
    didCreateRecord: function(store, type, record, json) {
        this.didSaveRecord(store, record, json);
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
        else if (name.charAt(name.length - 1) === 's')
            return name;
        else
            return name + 's';
    },

    /*
     Changes from default:
     - add trailing slash for lists.
     */
    buildURL: function(record, suffix) {
        var url = this._super(record, suffix);
        if (suffix === undefined && url.charAt(url.length - 1) !== '/') {
            url += '/';
        }
        return url;
    }

});

/*
Changes from default:
 - add embedded support
*/
var hasAssociation = function(type, options, one) {
    options = options || {};

    var meta = { type: type, isAssociation: true, options: options, kind: 'belongsTo' };

    return Ember.computed(function(key, value) {
        if (arguments.length === 2) {
            return value === undefined ? null : value;
        }

        var data = get(this, 'data').belongsTo,
            store = get(this, 'store'), id;

        if (typeof type === 'string') {
            type = get(this, type, false) || get(window, type);
        }

        id = data[key];

        // start: embedded support
        if (options.embedded == true && typeof(id) !== 'string') {
            // load the object
            var obj = data[key];
            if (obj !== undefined) {
                id = obj.id
                // Load the embedded object in store
                store.load(type, id, obj);
            }
        }
        // end: embedded support

        return id ? store.find(type, id) : null;
    }).property('data').meta(meta);
}

/*
Changes from default:
 - redefine belongsTo() with our own hasAssociation() function
*/
DS.belongsTo = function(type, options) {
    Em.assert("The type passed to DS.belongsTo must be defined", !!type);
    return hasAssociation(type, options);
};
