// We're gonna extend Backbone a bit...
// Let's get funky!


(function() {
    var Bluebone;
    Bluebone = this.Bluebone = Backbone;

    // We want all to be in our namespace
    Bluebone.routers = {};
    Bluebone.models = {};
    Bluebone.views = {};
    Bluebone.templates = {}; // underscore templates cache
    Bluebone.snippets = {}; // HTML snippets cache

    // Function to run after HTML is rendered
    Bluebone.afterRender; 


	/*
	 * ERRORS
	 */
	// Have one place to decide what to do with error messages.
	// In production we might not want to write those to console.
	Bluebone.logError = function(message, level) {
		if (undefined == level) {
			level = 'ERROR';
		}
		console.log(level + ': ' + message);
		return false;
	};


    /*
     * MODELS
     */
    // Shortcut to load a model class
    Bluebone.getModel = function(model) {
        if (undefined === Bluebone.models[model]) {
            Bluebone.logError('Model [' + model + '] not defined.');
        }
        return Bluebone.models[model];
    };

    // Add a Collection with REST connection for a given name
    Bluebone.createModel = function(name, cfg) {
        if (undefined == cfg || undefined == cfg.url) {
            Bluebone.logError('Need some configuration to set a resource. Try {url: <apiUrl>}');
        }
        if (undefined == cfg.method) {
            cfg.method = 'rest';
        }
        Bluebone.models[name] = new(Bluebone.Collection.extend(cfg));
        return Bluebone.models[name];
    };


    /*
     * TEMPLATES
     */
    // Load a template either from memory or through ajax
    Bluebone.loadTemplate = function(name, callback) {
        if (undefined == Bluebone.templates[name]) {
            $.get('/static/assets/global/tpl/' + name + '.tpl', function(data) {
                Bluebone.templates[name] = data;
                callback(data);
            });
        } else {
            callback(Bluebone.templates[name]);
        }

    };


    /*
     * VIEWS
     */
    // We set a standard behavior for our Views
    Bluebone.View = Backbone.View.extend({
        initialize: function() {
            return this;
        },
        renderTo: function(el, model) {
            Bluebone.loadTemplate(this.tpl, function(template){
                if (undefined == model) {
                    $(el).html(template);
	                if (undefined != Bluebone.afterRender) {
	                	Bluebone.afterRender(el);
	                }
                } else {
                    $(el).html(_.template(template, model.attributes));
	                if (undefined != Bluebone.afterRender) {
	                	Bluebone.afterRender(el);
	                }
                }
            });
            return this;
        }

    });

    // Get a view from views array. The view will be created if it's not in the
    // views array.
    // viewName: name of view to get
    // cfg: configuration with these parameters:
    //          tpl: template name (optional - defaults to viewName)
    Bluebone.getView = function(viewName, cfg) {
        if (undefined === Bluebone.views[viewName]) {
            Bluebone._createView(viewName, cfg);
        }
        return Bluebone.views[viewName];
    };

    // Private method.
    // Create and add a view to views array.
    Bluebone._createView = function(viewName, cfg) {
        if (undefined == cfg) {
            cfg = {};
        }
        // Use the same 'name' for template if none set.
        if (undefined === cfg.tpl) {
            cfg.tpl = viewName;
        }
        // Initiate the view
        Bluebone.views[viewName] = new (Bluebone.View.extend(cfg));
    };
    
    // Set the callback function to call after a view/snippet is rendered
    // This in mainly to run animations and other events on the 
    // the rendered HTML.
	Bluebone.setAfterRender = function(func) {
		Bluebone.afterRender = func;
	};

    // Get a list view from views array. The view will be created if it's not
    // in the views array.
    // viewName: name of view to get
    // cfg: configuration with these parameters:
    //          resource: resource to use (optional - defaults to viewName)
    //          itemViewName: the name of the itemView (optional - defaults to viewNameItem)
    //          url: the url for the API (required)
    //          order: the sort order (optional - currently not used)
    //          tpl: template name (optional - defaults to viewName)
    Bluebone.getListView = function(viewName, cfg) {
        if (undefined === Bluebone.views[viewName]) {
            Bluebone._createListView(viewName, cfg);
        }
        // TODO: check that the view in the array is actually a ListView because
        //       the views array has both ListViews and non-ListViews
        return Bluebone.views[viewName];
    };

    // Private method.
    // Create and add a ListView to the views array. This will also create and
    // add a view for each itemView.
    Bluebone._createListView = function(viewName, cfg) {
        if (undefined == cfg) {
            var cfg = {};
        }
        if (undefined == cfg.itemView) {
            cfg.itemView = viewName + 'Item';
        }
        if (undefined == cfg.tpl) {
            cfg.tpl = viewName;
        }
        if (undefined == cfg.resource) {
            cfg.resource = viewName;
        }
        var itemCfg = {tpl: cfg.itemView};
        Bluebone.views[cfg.itemView] = new(Bluebone.ListViewItem.extend(itemCfg));
        Bluebone.views[viewName] = new(Bluebone.ListView.extend(cfg));
    };


    // Create a view with a list of items
    // cfg will need 
    // url: Url to the API
    // resource: a name for the resource
    Bluebone.ListView = Bluebone.View.extend({
        class: 'list',
        initialize: function() {
        	if (undefined == this.resource) {
        		Bluebone.logError('We need a name for resource to initiate a ListView');
        	}
        	if (undefined == this.url) {
        		Bluebone.logError('We need a url for resource to initiate a ListView');
        	}
        	// Add a collection
            var collectionName = this.resource + 'Collection';
            this.collection = Bluebone.createModel(collectionName, {url: this.url});
            return this;
        },
        renderTo: function(el, params) {
        	if (undefined == params) {
        		params = {};
        	}
        	if (undefined == params.limit) {
        		params.limit = 9;
        	}
            var thisView = this;
            var ul = $('<ul></ul>').addClass(thisView.class);
            Bluebone.loadTemplate(thisView.tpl, function(template){
                $(el).html(_.template(template, {list: ul.wrap('<p>').parent().html()}));
            });
            this.collection.fetch({
            	data: params,
                success: function(){
                    var items = thisView.collection.models;
                    // Get the template for ListItems
                    // Rather do it here than in ItemView, so it's only loaded once
                    Bluebone.loadTemplate(thisView.itemView, function(template){
                        for (item in items) {
                            Bluebone.getView(thisView.itemView).render(template, items[item], function(item){
                                var li = $('<li />').append(item);
                                $('ul.' + thisView.class, el).append(li);
                            });
                        }
		                if (undefined != Bluebone.afterRender) {
		                	Bluebone.afterRender(el);
		                }
                    });
                }
            });

        }
    });

    // ListItemView. This should be only called from ListView
    Bluebone.ListViewItem = Bluebone.View.extend({
        initialize: function() {
            return this;
        },

        render: function(template, model, callback) {
            callback(_.template(template, model.attributes));
        }
    });


    // Load multiple views
    // 'view' is the view (view) to use
    // 'container' the DOM element to put it in
    Bluebone.views.load = function(cfg) {
        $.each(cfg, function(i, container) {
        	if (undefined == container.wrapper) {
				var target = $(container.container);        		
        	} else {
        		var wrapper = $('<' + container.wrapper + '/>');
        		if (container.className) {
        			wrapper.addClass(container.className);
        		}	
        		wrapper.appendTo(container.container);
        		var target = wrapper;
        	}
            $.each(container.widgets, function(j, widget) {
                if (target.children('#' + widget.name).attr('id')) {
                    Bluebone.logError('view ' + widget.name + ' already loaded...', 'info');
                } else {
                	if (undefined == widget.className) {
                		widget.className = 'widget';
                	};
                    $('<div />', {class: widget.className, id: widget.name}).appendTo(target);
                    Bluebone.getView(widget.name).renderTo('#' + widget.name);
                }
            });
        });
    };
    

	/*
	 * SNIPPETS
	 */
	// Special view for loading HTML snippets
    Bluebone.SnippetView = new (Backbone.View.extend({

        initialize: function() {
            return this;
        },

        renderTo: function(el, url) {
            Bluebone._loadSnippet(url, function(html) {
                $(el).html(html);
                if (undefined !== Bluebone.afterRender) {
                	Bluebone.afterRender(el);
                }
            });
            return this;
        }

    }));


    // Private method.
    // Load a html snippets either from memory or through ajax
    Bluebone._loadSnippet = function(url, callback) {
    	var name = url.replace(/\//g, ".");
        if (undefined == Bluebone.snippets[name]) {
            $.get(url, function(data) {
                Bluebone.snippets[name] = data;
                callback(data);
            });
        } else {
            callback(Bluebone.snippets[name]);
        }

    };

	Bluebone.renderSnippetTo = function(el, url){
		Bluebone.SnippetView.renderTo(el, url);
	};



}).call(this);