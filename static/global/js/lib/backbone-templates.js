/**
 * Backbone-tastypie.js 0.1
 * (c) 2011 Paul Uithol
 * 
 * Backbone-tastypie may be freely distributed under the MIT license.
 * Add or override Backbone.js functionality, for compatibility with django-tastypie.
 */
(function( undefined ) {
	"use strict";

	// Backbone.noConflict support. Save local copy of Backbone object.
	var Backbone = window.Backbone;


	Backbone.Templates = {
	  	templates: {},
	  	/*
	  	cfg : {
			tplDir: '/static/global/tpl/',
			tplSuffix: '.html'
	
	  	},
	  	*/
		get: function(tpl, callback){
			var template = this.templates[tpl];
			if (template) {
  				callback(template);
			} else {
	  			var that = this;
	  			$.get("/templates/" + tpl + ".html", function(template){
	        		var $tmpl = $(template);
	        		that.templates[tpl] = $tmpl;
	        		callback($tmpl);
	      		});
    		}

  		}

	}
})();
