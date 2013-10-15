// Taken and adapted from https://gist.github.com/iStefo/5481507

(function() {
// TODO: keywords!
Ember.onLoad('Ember.Application', function(Application) {
  Application.initializer({
    name: "meta",
   
    initialize: function(container, application) {
      // helper function to get tag from dom
      var _getTag = function(tagname, property, value) {
        var selector = tagname+"["+property+'="'+value+'"]';
        var tags = $(selector);
        if (tags.length){
          return $(tags[0]);
        }
      };
   
      // hold logic and information
      var Meta = Ember.Object.extend(Ember.Evented, {
        application: null,
   
        // string values
        title: null,
        description: null,
        keywords: null,
   
        // dom elements (jQuery objects)
        _ogTitle: null,
        _description: null,
        _ogDescription: null,
        _ogKeywords: null,
   
        // defaults, set by the base template
        defaults: {
          title: default_title,
          description: default_description,
          keywords: default_keywords
        },
   
        summary: Ember.computed(function() {
          return '<title>' + this.get('title') + '</title>\n' +
            this.get('_ogTitle').outerHTML + '\n' +
            this.get('_description').outerHTML + '\n' +
            this.get('_ogDescription').outerHTML;
        }).property('_ogTitle', '_ogDescription'),
   
        // propagate changes to dom elements
        titleChanged: function() {
          document.title = this.get('title');
          this.get('_ogTitle').attr('content', this.get('title'));
        }.observes('title'),
   
        descriptionChanged: Ember.observer(function() {
          this.get('_description').attr('content', this.get('description'));
          this.get('_ogDescription').attr('content', this.get('description'));
          this.notifyPropertyChange('_ogDescription');
        }, 'description'),

        keywordsChanged: Ember.observer(function() {
          this.get('_keywords').attr('content', this.get('keywords'));
          this.get('_ogKeywords').attr('content', this.get('keywords'));
          this.notifyPropertyChange('_ogkeywords');
        }, 'keywords'),
   
        init: function() {
          this._super();
          this.on('reloadDataFromRoutes', this.reloadDataFromRoutes);
        },
   
        reloadDataFromRoutes: function() {
          var handlers = this.get('application').Router.router.currentHandlerInfos,
            newTitle,
            newDescription,
            newKeywords,
            i = handlers.length;
          // walk through handlers until we have title and description
          // take the first ones that are not empty
          while (i--) {
            var handler = handlers[i].handler;
            if (!newTitle) {
              var handlerTitle = Ember.get(handler, 'metaTitle');
              if(handlerTitle){
                newTitle = handlerTitle + ' | ' + this.get('defaults.title');
              } else {
                newTitle = this.get('defaults.title');
              }
            }
            if (!newDescription) {
              newDescription = Ember.get(handler, 'metaDescription');
            }
            if(!newKeywords){
              newKeywords = Ember.get(handler, 'metaKeywords');
            }
          }
          // save changes or snap back to defaults
          if (newTitle) {
            this.set('title', newTitle);
          } else if (this.get('defaults.title')) {
            this.set('title', this.get('defaults.title'));
          }
          if (newDescription) {
            this.set('description', newDescription);
          } else if (this.get('defaults.description')) {
            this.set('description', this.get('defaults.description'));
          }
          if(newKeywords) {
            this.set('keywords', newKeywords);
          } else if (this.get('defaults.keywords')) {
            this.set('keywords', this.get('defaults.keywords'));
          }
          this.trigger('didReloadDataFromRoutes');
        }
      });
      var meta = Meta.create({application: application});

      // TODO: description
      // meta.set('defaults.title', document.title);
   
      // setup meta object
      // are there any tags present yet? if not, create them
      // ogTitle
      var _ogTitle = _getTag('meta', 'property', 'og:title');
      if (!_ogTitle) {
        _ogTitle = document.createElement('meta');
        _ogTitle.setAttribute('property', 'og:title');
        document.head.appendChild(_ogTitle);
        _ogTitle = $(_ogTitle);
      }
      meta.set('_ogTitle', _ogTitle);
   
      // description
      var _description = _getTag('meta', 'name', 'description');
      if (!_description) {
        _description = document.createElement('meta');
        _description.setAttribute('name', 'description');
        document.head.appendChild(_description);
        _description = $(_description);
      } else {
        meta.set('defaults.description', _description.attr('content'));
      }
      meta.set('_description', _description);
      
      // ogDescription
      var _ogDescription = _getTag('meta', 'property', 'og:description');
      if (!_ogDescription) {
        _ogDescription = document.createElement('meta');
        _ogDescription.setAttribute('property', 'og:description');
        document.head.appendChild(_ogDescription);
        _ogDescription = $(_ogDescription);
      } else {
        meta.set('defaults.description', _ogDescription.content);
      }
      meta.set('_ogDescription', _ogDescription);

      // keywords
      var _keywords = _getTag('meta', 'name', 'keywords');
      if (!_keywords) {
        _keywords = document.createElement('meta');
        _keywords.setAttribute('name', 'keywords');
        document.head.appendChild(_keywords);
        _keywords = $(_keywords);
      } else {
        meta.set('defaults.keywords', _keywords.content);
      }
      meta.set('_keywords', _keywords);
   
      // ogKeywords
      var _ogKeywords = _getTag('meta', 'property', 'og:keywords');
      if (!_ogKeywords) {
        _ogKeywords = document.createElement('meta');
        _ogKeywords.setAttribute('property', 'og:keywords');
        document.head.appendChild(_ogKeywords);
        _ogKeywords = $(_ogKeywords);
      } else {
        meta.set('defaults.keywords', _ogKeywords.attr('content'));
      }
      meta.set('_ogKeywords', _ogKeywords);

      // save object to app
      application.set('meta', meta);
    }
  });
});

})();