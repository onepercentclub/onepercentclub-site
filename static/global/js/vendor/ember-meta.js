// Taken and adapted from https://gist.github.com/iStefo/5481507

(function() {
Ember.onLoad('Ember.Application', function(Application) {
  Application.initializer({
    name: "meta",
   
    initialize: function(container, application) {
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
        url: null,
        image: null,
   
        // dom elements (jQuery objects)
        _ogTitle: null,
        _description: null,
        _ogDescription: null,
        _ogKeywords: null,
        _ogUrl: null,
        _ogImage: null,
   
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

        urlChanged: Ember.observer(function() {
          this.get('_ogUrl').attr('content', this.get('url'));
          this.notifyPropertyChange('_ogUrl');
        }, 'url'),

        imageChanged: Ember.observer(function() {
          this.get('_ogImage').attr('content', this.get('image'));
        }, 'image'),
   
        init: function() {
          this._super();
          this.on('reloadDataFromRoutes', this.reloadDataFromRoutes);
        },
   
        reloadDataFromRoutes: function() {
          var handlers = this.get('application').Router.router.currentHandlerInfos,
            newTitle,
            newDescription,
            newKeywords,
            newImage,
            i = handlers.length;
          // walk through handlers until we have title and description
          // take the first ones that are not empty
          while (i--) {
            var handler = handlers[i].handler;
            var currentModel = Ember.get(handler, 'currentModel');

            if(currentModel){
              var meta_data = Ember.get(currentModel, 'meta_data');
              if(meta_data){
                if (!newTitle) {
                  var handlerTitle = meta_data.title;
                  if(handlerTitle){
                    newTitle = handlerTitle + ' | onepercentclub.com'; // TODO: avoid hardcoding this
                  } else {
                    newTitle = this.get('defaults.title');
                  }
                }
                if (!newDescription) {
                  newDescription = meta_data.description;
                }
                if(!newKeywords){
                  newKeywords = meta_data.keywords;
                }
                if (!newImage && meta_data.image) {
                  newImage = meta_data.image.full;
                }
              }
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
          if(newImage) {
            this.set('image', newImage);
          } else if (this.get('defaults.image')) {
            this.set('image', this.get('defaults.image'));
          }

          this.set('url', window.location.href);


          this.trigger('didReloadDataFromRoutes');
        }
      });
      var meta = Meta.create({application: application});

      meta.set('defaults.title', document.title);
   
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

      var _ogUrl = _getTag('meta', 'property', 'og:url');
      if (!_ogUrl) {
        _ogUrl = $(document.createElement('meta'));
        $('head').append(_ogUrl);
        _ogUrl.attr('property', 'og:url');
      }
      meta.set('_ogUrl', _ogUrl);
   
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
      }
      meta.set('_ogKeywords', _ogKeywords);

      // ogImage
      var _ogImage = _getTag('meta', 'property', 'og:image');
      if (!_ogImage) {
        _ogImage = document.createElement('meta');
        _ogImage.setAttribute('property', 'og:image');
        document.head.appendChild(_ogImage);
        _ogImage = $(_ogImage);
      } else {
        meta.set('defaults.ogImage', _ogImage.attr('content'));
      }
      meta.set('_ogImage', _ogImage);


      // save object to app
      application.set('meta', meta);
    }
  });
});

})();