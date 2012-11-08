var get = Ember.get, set = Ember.set;

DS.DRF2Serializer = DS.Serializer.extend({


  getItemUrl: function(meta, id){
    var url;

    url = get(this, 'adapter').rootForType(meta.type);
    return ["", get(this, 'namespace'), url, id, ""].join('/');
  },


  keyForBelongsTo: function(type, name) {
    return this.keyForAttributeName(type, name) + "_id";
  },

  keyForAttributeName: function(type, name) {
    return Ember.String.decamelize(name);
  },

  /**
    ASSOCIATIONS: SERIALIZATION
    Transforms the association fields to Resource URI django-tastypie format
  */
  addBelongsTo: function(hash, record, key, relationship) {
    var id = get(record, relationship.key+'.id');
    if (!Ember.none(id)) { hash[key] = this.getItemUrl(relationship, id); }
  },

  addHasMany: function(hash, record, key, relationship) {
    var self = this,
        serializedValues = [],
        id = null;

    key = this.keyForHasMany(relationship.type, key);

    value = record.get(key) || [];

    value.forEach(function(item) {
      id = get(item, self.primaryKey(item));
      serializedValues.push(self.getItemUrl(relationship, id));
    });

    hash[key] = serializedValues;
  },

  /**
    ASSOCIATIONS: DESERIALIZATION
    Transforms the association fields from Resource URI django-tastypie format
  */
  _deurlify: function(value) {
    if (!!value) {
      return value.split('/').reverse()[1];
    }
  },

  extractHasMany: function(record, hash, relationship) {
    var value,
        self = this,
        key = this._keyForHasMany(record.constructor, relationship.key);

    value = hash[key];

    if (!!value) {
      value.forEach(function(item, i, collection) {
        collection[i] = (relationship.options.embedded) ? item : self._deurlify(item);
      });
    }

    return value;
  },

  extractBelongsTo: function(record, hash, relationship) {
    //var key = this._keyForBelongsTo(record.constructor, relationship.key);
    var key = relationship.key;
    var value = hash[key];
    if (!!value) {
      value = (relationship.options.embedded) ? value : this._deurlify(value);
    }
    return value;
  }

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

