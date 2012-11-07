DS.DRF2Adapter = DS.RESTAdapter.extend({
  namespace: "i18n/api",

  didFindAll: function(store, type, json) {
    store.loadMany(type, json.results);
    store.didUpdateAll(type);
  },

  didFindRecord: function(store, type, json, id) {
    store.load(type, id, json);
  },

});

