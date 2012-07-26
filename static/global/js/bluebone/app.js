// We're gonna extend Backbone a bit...
// Let's get funky!


(function() {
    var Bluebone;
    Bluebone = this.Bluebone = Backbone;

    // We want all to be in our namespace
    Bluebone.routers = {};
    Bluebone.models = {};
    Bluebone.views = {};
    Bluebone.templates = {};
    Bluebone.snippets = {};


    /* MODELS */

    // Shortcut to load a model class
    Bluebone.models.get = function(model) {
        if (undefined === Bluebone.models[model]) {
            console.log('Model [' + model + '] not defined.');
        }
        return Bluebone.models[model];
    };

    // Add a Collection with REST connection for a given name
    Bluebone.models.newApiCollection = function(name, cfg) {
        if (undefined == cfg || undefined == cfg.url) {
            console.log('Need some configuration to set a resource. Trye {url: <apiUrl>}');
        }
        if (undefined == cfg.method) {
            cfg.method = 'rest'
        }
        Bluebone.models[name] = new(Bluebone.Collection.extend(cfg));
        return Bluebone.models[name];
    };

    /* TEMPLATES */

    // Load a template either from memory or through ajax
    Bluebone.templates.load = function(name, callback) {
        if (undefined == Bluebone.templates[name]) {
            console.log('Load template: ' + name);
            $.get('/static/assets/global/tpl/' + name + '.tpl', function(data) {
                Bluebone.templates[name] = data;
                //console.log(Bluebone.templates[name]);
                callback(data);
            });
        } else {
            callback(Bluebone.templates[name]);
        }

    }

    /* SNIPPETS */

    // Load a html snippets either from memory or through ajax
    Bluebone.snippets.load = function(url, callback) {
    	var name = url.replace(/\//g, ".");
        if (undefined == Bluebone.templates[name]) {
            console.log('Load template: ' + name + ' : ' + url);
            $.get(url, function(data) {
                Bluebone.templates[name] = data;
                //console.log(Bluebone.templates[name]);
                callback(data);
            });
        } else {
            callback(Bluebone.templates[name]);
        }

    }


    /* VIEWS */


    // We set a standard behavior for our Views
    Bluebone.View = Backbone.View.extend({

        initialize: function() {
            return this;
        },

        renderTo: function(el, model) {
            var self = this;
            Bluebone.templates.load(this.tpl, function(template){
                if (undefined == model) {
                    $(el).html(template);
	                if (undefined != Bluebone.views.callback) {
	                	Bluebone.views.callback(el);
	                }
                } else {
                    $(el).html(_.template(template, model.attributes));
	                if (undefined != Bluebone.views.callback) {
	                	Bluebone.views.callback(el);
	                }
                }
            });
            return this;
        },

    });


	
    // Get a view from views array
    Bluebone.views.get = function(view) {
        if (undefined === Bluebone.views[view]) {
            console.log('View [' + view + '] not loaded!');
        }
        return Bluebone.views[view];
    };

    // Add a view to views array
    Bluebone.views.add = function(name, cfg) {
        if (undefined == cfg) {
            cfg = {};
        }
        if (undefined === cfg.tpl) {
            cfg.tpl = name;
        }
        Bluebone.views[name] = new (Bluebone.View.extend(cfg));
    };


	// Special view for loading HTML snippets
    Bluebone.snippets.View = new (Backbone.View.extend({

        initialize: function() {
            return this;
        },

        renderTo: function(el, url) {
            var self = this;
            Bluebone.snippets.load(url, function(html){
                $(el).html(html);
                if (undefined != Bluebone.snippets.callback) {
                	Bluebone.snippets.callback(el);
                }
            });
            return this;
        },

    }));

	Bluebone.snippets.renderTo = function(el, url){
		Bluebone.snippets.View.renderTo(el, url);
	}

	Bluebone.snippets.setCallback = function(func) {
		Bluebone.snippets.callback = func;
	}

	Bluebone.views.setCallback = function(func) {
		Bluebone.views.callback = func;
	}


    Bluebone.views.addList = function(name, cfg) {
        if (undefined == cfg) {
            var cfg = {};
        }
        if (undefined == cfg.itemView) {
            cfg.itemView = name + 'Item';
        }
        if (undefined == cfg.tpl) {
            cfg.tpl = name
        }
        var itemCfg = {tpl: cfg.itemView};
        Bluebone.views[cfg.itemView] = new(Bluebone.ListItemView.extend(itemCfg));
        Bluebone.views[name] = new(Bluebone.Listview.extend(cfg));
    }



    // Create a view with a list of items
    // specify a api-url
    Bluebone.Listview = Bluebone.View.extend({
        class: 'list',
        initialize: function() {
            var collectionName = this.resource + 'Collection';
            this.collection = Bluebone.models.newApiCollection(collectionName, {test: 'test', url: this.url});
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
            Bluebone.templates.load(thisView.tpl, function(template){
                $(el).html(_.template(template, {list: ul.wrap('<p>').parent().html()}));
            });
            this.collection.fetch({
            	data: params,
                success: function(){
                    var items = thisView.collection.models;
                    // Get the template for ListItems
                    Bluebone.templates.load(thisView.itemView, function(template){
                        for (item in items) {
                            Bluebone.views.get(thisView.itemView).render(template, items[item], function(item){
                                var li = $('<li />').append(item);
                                $('ul.' + thisView.class, el).append(li);
				                if (undefined != Bluebone.views.callback) {
				                	Bluebone.views.callback(el);
				                }
                            })

                        }
                    });
                }
            });

        }
    });

    // ListItemView. This should be only called from ListView
    Bluebone.ListItemView = Bluebone.View.extend({
        initialize: function() {
            return this;
        },

        render: function(template, model, callback) {
            callback(_.template(template, model.attributes));
        }
    });


    // Load mulitple views
    // cfg should be in te for of :
    // [{
    //      view: 'RecentProjects',
    //      container: '#midpanel'
    //  },
    //  {
    //      view: 'About',
    //      container: '#midpanel'
    //  },
    //]
    // 'view' is the view (view) to use
    // 'container' the DOM element to put it in
    Bluebone.views.load = function(cfg) {
        $.each(cfg, function(i, container){
        	if (undefined == container.wrapper) {
				var target = $(container.container);        		
        	} else {
        		var wrapper = $('<' + container.wrapper + '/>');
        		if (container.className) {
        			wrapper.addClass(container.className);
        		}	
        		wrapper.appendTo(container.container)
        		var target = wrapper;
        	}
            $.each(container.widgets, function(j, widget) {
                if (target.children('#' + widget.name).attr('id')) {
                    console.log('view ' + widget.name + ' already loaded...');
                } else {
                	if (undefined == widget.className) {
                		widget.className = 'widget';
                	};
                    $('<div />', {class: widget.className, id: widget.name}).appendTo(target);
                    Bluebone.views.get(widget.name).renderTo('#' + widget.name);
                }
            });
        });
    };


}).call(this);