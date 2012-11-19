var get = Ember.get, set = Ember.set;

DS.DRF2Serializer = DS.Serializer.extend({

// TODO: Remove this serializer stuff we're not using. Removing it causes things to fail.

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
  Ember.assert("The type passed to DS.belongsTo must be defined", !!type);
  return hasAssociation(type, options);
};

