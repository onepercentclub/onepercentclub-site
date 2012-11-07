var get = Ember.get, set = Ember.set;

DS.DjangoTastypieSerializer = DS.Serializer.extend({
    getItemUrl: function(meta, id){
        var url;
        
        url = get(this, 'adapter').rootForType(meta.type);
        return ["", get(this, 'namespace'), url, id, ""].join('/');
    },
});

DS.DRF2Adapter = DS.RESTAdapter.extend({
  serverDomain: null,
  namespace: "i18n/api",
  bulkCommit: false,
  serializer: DS.DRF2Serializer,

  didFindAll: function(store, type, json) {
    store.loadMany(type, json.results);
    store.didUpdateAll(type);
  },

  didFindQuery: function(store, type, json, recordArray) {
    //var root = this.pluralize(this.rootForType(type));
    //this.sideload(store, type, json, root);
    //recordArray.load(json[root]);
    store.loadMany(type, json.results);
    store.didUpdateAll(type);

  },

  didFindRecord: function(store, type, json, id) {
    store.load(type, id, json);
  },


});

