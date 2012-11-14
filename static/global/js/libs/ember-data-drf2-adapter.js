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

// TODO: Remove this serializer stuff we're not using. Removing it causes things to fail.

  init: function() {
    // By default, the JSON types are passthrough transforms
    this.transforms = {
      'string': passthrough,
      'number': passthrough,
      'boolean': passthrough,
      'array':  {
                fromJSON: function(serialized) {
                  return Ember.none(serialized) ? null : eval(serialized);
                },
    
                toJSON: function(deserialized) {
                  return Ember.none(deserialized) ? null : deserialized.toJSON();
                }
            }
    };
    this.mappings = Ember.Map.create();
  },

    

});



DS.DRF2Adapter = DS.RESTAdapter.extend({
  namespace: "i18n/api",

  // If you want to remove our DRF2 serializer use this instead:
  // serializer: DS.RESTSerializer,
  serializer: DS.DRF2Serializer,

  init: function() {
    var serializer,
        namespace;

    this._super();

    namespace = get(this, 'namespace');
    Em.assert("tastypie namespace parameter is mandatory.", !!namespace);

    // Make the adapter available for the serializer
    serializer = get(this, 'serializer');
    set(serializer, 'adapter', this);
    set(serializer, 'namespace', namespace);
  },

  didFindAll: function(store, type, json) {
    // If there's multiple items they
    // will be in .results
    if (json.results) {
        store.loadMany(type, json.results);
    } else {
        var id = json.id ? json.id : null;
        var result = store.load(type, id, json);
        console.log(result);
    }
    store.didUpdateAll(type);
  },

  didFindRecord: function(store, type, json, id) {
    store.load(type, id, json);
  },

  createRecord: function(store, type, record) {
    var data, root = this.rootForType(type);

    data = record.toJSON();

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
    if (type.url){
        return type.url;
    }  
    var object = new type;
    if (object['url']){
        return object['url']; 
    }
    // use the last part of the name as the URL
    var parts = type.toString().split(".");
    var name = parts[parts.length - 1];
    return name.replace(/([A-Z])/g, '_$1').toLowerCase().slice(1);
  },

  pluralize: function(name) {
    return name;
  },

  loadValue: function(store, type, value) {
    if (value instanceof Array) {
      store.loadMany(type, value);
    } else {
      store.load(type, value);
    }
  },


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

    var id = data[key];
    if (options.embedded == true && typeof(id) !== 'string') {
        var obj = data[key];
        if (obj !== undefined) {
            id = obj.id ? obj.id : obj.name ? obj.name : obj.username;
            store.load(type, id, obj);
        }
    }
    return id ? store.find(type, id) : null;
  }).property('data').meta(meta);
};

DS.belongsTo = function(type, options) {
  Ember.assert("The type passed to DS.belongsTo must be defined", !!type);
  return hasAssociation(type, options);
};
