/*
 * DataSource abstraction inspired by these sources:
 *  http://jzajpt.github.com/2012/01/24/emberjs-app-architecture-data.html
 *  https://github.com/escalant3/ember-data-tastypie-adapter
 */

App.DataSource = Em.Object.extend({
    apiUrl: "/i18n/api/",

    get: function(url, query, callback) {
        this._ajax(url, "GET", {
            data: query,
            success: function (json) {
                callback(json);
            }
        });
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
