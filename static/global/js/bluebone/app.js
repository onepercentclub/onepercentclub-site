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
	            Bluebone.templates[name] = _.template(data);
	            callback(Bluebone.templates[name]);
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
		
		Bluebone.models[name] = Bluebone.Model.extend(cfg);
		var collectionName = name + 'Collection';
		var rootUrl = cfg.url;
		Bluebone.models[name] = Bluebone.Model.extend(cfg);
	}
	
	// We set a standard behaviour for our Views
	Bluebone.View = Backbone.View.extend({
		
	    initialize: function() {
	    	return this;
	    },
	    
	    renderTo: function(el) {
	    	var self = this;
	    	Bluebone.templates.load(this.tpl, function(template){
		    	$(el).html(template);
	    	});
	        return this;
	    },	
	    
	});


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
	            $(el).html(template);
	    	});
	        return this;
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