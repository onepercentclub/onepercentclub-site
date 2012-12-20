var get = Ember.get, set = Ember.set;

var passthrough = {
    fromJSON: function(value) {
        return value;
    },

    toJSON: function(value) {
        return value;
    }
};


DS.DRF2Serializer = DS.Serializer.extend({

    init: function() {
        // By default, the JSON types are passthrough transforms
        this.transforms = {
            'string': passthrough,
            'number': passthrough,
            'boolean': passthrough,
            'array': {
                fromJSON: function(serialized) {
                    return Ember.none(serialized) ? null : eval(serialized);
                },

                toJSON: function(deserialized) {
                    return Ember.none(deserialized) ? null : deserialized.toJSON();
                }
            }
        };
        this.mappings = Ember.Map.create();
    }

});


DS.DRF2Adapter = DS.RESTAdapter.extend({
    namespace: "i18n/api",

    serializer: DS.DRF2Serializer,

    init: function() {
        var serializer,
            namespace;

        this._super();

        namespace = get(this, 'namespace');
        // Make the adapter available for the serializer
        serializer = get(this, 'serializer');
        set(serializer, 'adapter', this);
        set(serializer, 'namespace', namespace);
    },


    didFindAll: function(store, type, json) {
        // If there's multiple items they will be in .results
        if (json.results) {
            store.loadMany(type, json.results);
        } else {
            var id = json.id ? json.id : null;
            var result = store.load(type, id, json);
        }
        store.didUpdateAll(type);
    },

    didFindRecord: function(store, type, json, id) {
        store.load(type, id, json);
    },

    didFindQuery: function(store, type, json, recordArray) {
        recordArray.load(json.results);
    },

    createRecord: function(store, type, record) {
        var root = this.rootForType(type);
        var data = record.toJSON();

        this.ajax(this.buildURL(root), "POST", {
            data: data,
            success: function(json) {
                this.didCreateRecord(store, record, json);
            }
        });
    },

    didCreateRecord: function(store, type, record, json) {
        this.sideload(store, type, json);
        // TODO: make sure local store-record is updated with json response
        //store.didSaveRecord(record, json);
    },


    rootForType: function(type) {
        if (type.url) {
            return type.url;
        }
        var object = new type;
        if (object['url']) {
            return object['url'];
        }
        Em.assert("The model " + type + " must define a 'url' field for the API resource.", false);
    },

    pluralize: function(name) {
        // Our pluralize method does nothing because we're manually defining out API resource locations in the url field.
        return name;
    },

    loadValue: function(store, type, value) {
        if (value instanceof Array) {
            store.loadMany(type, value);
        } else {
            store.load(type, value);
        }
    },

    findQuery: function(store, type, query, recordArray) {
        // This is the same as the parent function with an added trailing slash on root.
        var root = this.rootForType(type) + '/';

        this.ajax(this.buildURL(root), "GET", {
            data: query,
            success: function(json) {
                this.didFindQuery(store, type, json, recordArray);
            }
        });
    }

});

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

        // Mind you! This might be an ID or an entire object
        var id = data[key];

        // This is our addition to make 'embedded' option work

        // Only do embedded if we have an object here
        if (options.embedded == true && typeof(id) !== 'string') {
            // load the object
            var obj = data[key];
            if (obj !== undefined) {
                // Guess the primary key
                // TODO: revert to defined primaryKey
                id = obj.id ? obj.id : obj.name ? obj.name : obj.username;
                // Load the embedded object in store
                store.load(type, id, obj);
            }
        }
        // End of our addition
        return id ? store.find(type, id) : null;
    }).property('data').meta(meta);
};

// Redefine belongsTo again with our own hasAssociation function
DS.belongsTo = function(type, options) {
    Em.assert("The type passed to DS.belongsTo must be defined", !!type);
    return hasAssociation(type, options);
};
