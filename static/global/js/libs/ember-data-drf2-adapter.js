var get = Ember.get, set = Ember.set;

DS.DRF2Serializer = DS.Serializer.extend({

// TODO: Remove this serializer stuff we're not using. Removing it causes things to fail.

});



DS.DRF2Adapter = DS.RESTAdapter.extend({
  namespace: "i18n/api",

/**
    Serializer object to manage JSON transformations
  */
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
    store.loadMany(type, json.results);
    store.didUpdateAll(type);
  },

  didFindRecord: function(store, type, json, id) {
    store.load(type, id, json);
  },

  rootForType: function(type) {
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

