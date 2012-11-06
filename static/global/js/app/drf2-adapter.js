var get = Ember.get, set = Ember.set;

DS.DRF2Adapter = DS.RESTAdapter.extend({
  serverDomain: null,
  namespace: "i18n/api",
  bulkCommit: false,

  didFindAll: function(store, type, json) {
    store.loadMany(type, json.results);
    store.didUpdateAll(type);
  },

  didFindQuery: function(store, type, json, recordArray) {
    var root = this.pluralize(this.rootForType(type));
    this.sideload(store, type, json, root);
    recordArray.load(json[root]);
  },

  didFindRecord: function(store, type, json, id) {
    var root = this.rootForType(type);
    this.sideload(store, type, json, root);
    store.load(type, id, json[root]);
  },


});

