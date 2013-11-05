// Custom Assertions
pavlov.specify.extendAssertions({
    isDSArray: function(actual, message) {
        ok(actual.toString().match(/DS\.ManyArray/), message);
    },
    isFunction: function(actual, message) {
        ok(typeof actual == 'function', message);
    },
    isEmptyArray: function(actual, message) {
        ok(!actual.length, message);
    }
});