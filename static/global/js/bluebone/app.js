// We're gonna extend Backbone a bit...
// Let's get funky!

(function() {
	var Bluebone;
	Bluebone = this.Bluebone = Backbone;
	
	// We want all to be in our namespace
	Bluebone.routers = {};
	Bluebone.models = {};
	Bluebone.views = {};
	Bluebone.widgets = {};
	Bluebone.templates = {};
	

	// Load a template either from memory or through ajax
	Bluebone.templates.load = function(name, callback) {
		if (undefined == Bluebone.templates[name]) {
			$.get('/static/global/tpl/' + name + '.html', function(data) {
	            Bluebone.templates[name] = data;
				//console.log(Bluebone.templates[name]);
	            callback(data);
	        });			 
		} else {
	        callback(Bluebone.templates[name]);
		}	

	}

	// Add a Model and Collection with REST connection for a given name
	Bluebone.models.addApiResource = function(name, cfg) {
		if (undefined == cfg || undefined == cfg.url) {
			console.log('Need some configuration to set a resource. Trye {url: <apiUrl>}');
		}
		if (undefined == cfg.method) {
			cfg.method = 'rest'
		}
		cfg.rootUrl = cfg.url;
		Bluebone.models[name] = Bluebone.Model.extend(cfg);
		//cfg.model = Bluebone.models[name];
		var collectionName = name + 'Collection';
		Bluebone.models[collectionName] = Bluebone.Model.extend(cfg);
	}
	
	Bluebone.widgets.addListWidget = function(name, cfg) {
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
		Bluebone.widgets[name] = new(Bluebone.ListWidget.extend(cfg));
	}
	
	
	// We set a standard behavior for our Views
	Bluebone.View = Backbone.View.extend({
		
	    initialize: function() {
	    	return this;
	    },
	    
	    renderTo: function(el, model) {
	    	var self = this;
	    	Bluebone.templates.load(this.tpl, function(template){
	    		//console.log(model);
	    		if (undefined == model) {
			    	$(el).html(template);
	    		} else {
			    	$(el).html(_.template(template, model.attributes));
	    		}
	    	});
	        return this;
	    },	
	    
	});


	// Shortcut to load a model class
	Bluebone.models.get = function(model) {
		if (undefined === Bluebone.models[model]) {
			console.log('Model [' + model + '] not defined.');
		}
		return Bluebone.models[model];
	};

	// Shortcut to load a view instance
	Bluebone.views.get = function(view) {
		if (undefined === Bluebone.views[view]) {
			console.log('View [' + view + '] not loaded!');
		}
		return Bluebone.views[view];
	};
	
	Bluebone.views.add = function(name, cfg) {
		if (undefined == cfg) {
			cfg = {};
		}
		if (undefined === cfg.tpl) {
			cfg.tpl = name;
		} 
		Bluebone.views[name] = new (Bluebone.View.extend(cfg));
	};
	

	// A custom View for our Widgets	
	Bluebone.Widget = Bluebone.View.extend({
	    initialize: function() {
	    	return this;
	    },
	    
	    renderTo: function(el){
	    	var tpl = this.tpl;
	    	Bluebone.templates.load(this.tpl, function(template){
	            $(el).html(_.template(template));
	    	});
	        return this;
	    },			
	});



	Bluebone.ListWidget = Bluebone.View.extend({
		class: 'list',
	    initialize: function() {
	    	if (undefined === this.itemView) {
	    		console.log('No itemView set for ListWidget ' + this.tpl);
	    	};
	    	if (undefined === this.resource) {
	    		console.log('No resource set for ListWidget ' + this.tpl);
	    	}
	    	var collectionName = this.resource + 'Collection';
	    	//this.collection = new Bluebone.models.get(this.resource + 'Collection');
	    	this.collection = new (Backbone.Collection.extend({url: '/projects/api/project'}))
	    	
	    	return this;
	    },
		renderTo: function(el) {
			var thisView = this;
			var ul = $('<ul></ul>').addClass(thisView.class);
	    	Bluebone.templates.load(thisView.tpl, function(template){
				$(el).html(_.template(template, {list: ul.wrap('<p>').parent().html()}));
			});			
			this.collection.fetch({
				success: function(){
					var items = thisView.collection.models;
					for (item in items) {
						Bluebone.views.get(thisView.itemView).html(items[item], function(item){
							$(el).children('ul.'+thisView.class).append(item);	
						})
						
					}
				}
			});
			
		}		
	});


	Bluebone.ListItemView = Bluebone.View.extend({
		initialize: function() {
			return this;
		},

	    html: function(model, callback) {
	    	var html;
	    	Bluebone.templates.load(this.tpl, function(template){
		    	callback(_.template(template, model.attributes));
	    	});
	    },
	});

	// Shortcut to load a widget instance from array
	Bluebone.widgets.get = function(widget) {
		if (undefined === Bluebone.widgets[widget]) {
			console.log('Widget [' + widget + '] not loaded!');
		}
		return Bluebone.widgets[widget];
	};

	Bluebone.widgets.add = function(name, cfg) {
		if (undefined == cfg) {
			cfg = {};
		}
		if (undefined === cfg.tpl) {
			cfg.tpl = name;
		} 
		Bluebone.widgets[name] = new (Bluebone.Widget.extend(cfg));
	};
	

	// Load mulitple widgets
	// cfg should be in te for of :
	// [{
	//		widget: 'RecentProjects',
	//		container: '#midpanel'
	//	},
	//	{
	//		widget: 'About',
	//		container: '#midpanel'
	//	},
	//]
	// 'widget' is the widget (view) to use
	// 'container' the DOM element to put it in
	Bluebone.widgets.load = function(cfg) {
		$.each(cfg, function(i, wdg){
			if ($(wdg.container).children('#' + wdg.widget).attr('id')) {
				console.log('Widget ' + wdg.widget + ' already loaded...');
			} else {
				$('<div />', {class: 'widget', id: wdg.widget}).appendTo(wdg.container);
				Bluebone.widgets.get(wdg.widget).renderTo('#' + wdg.widget);
			}
		});
	};


}).call(this);