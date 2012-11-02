/*
 * DataSource abstraction inspired by these sources:
 *  http://jzajpt.github.com/2012/01/24/emberjs-app-architecture-data.html
 *  https://github.com/escalant3/ember-data-tastypie-adapter
 */

App.DataSource = Em.Object.extend({
    apiUrl: "/i18n/api/",
    templateUrl: "/en/templates/",
    templatePostfix: ".hb.html",

    get: function(url, query, callback) {
        this._ajax(url, "GET", {
            data: query,
            success: function (json) {
                callback(json);
            }
        });
    },

    getTemplate: function(template, callback) {
        var hash = {};
        hash.url = this.templateUrl + template + this.templatePostfix;
        hash.type = 'GET';
        hash.dataType = 'html';
        hash.contentType = 'application/json';
        hash.success = callback;
        jQuery.ajax(hash);
    },

    post: function(url, query, callback) {
//        TODO: implement
    },

    put: function(url, query, callback) {
//        TODO: implement
    },

    _ajax: function(url, type, hash) {
        if (url.match('^http') || url.match('^\/')) {
            hash.url = url;
        } else {
            hash.url = this.apiUrl + url;
        }
        hash.type = type;
        hash.dataType = "json";
        hash.contentType = 'application/json';
        jQuery.ajax(hash);
    }

});

App.dataSource = App.DataSource.create();
