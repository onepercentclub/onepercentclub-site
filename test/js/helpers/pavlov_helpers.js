// Custom Assertions
pavlov.specify.extendAssertions({
    isDSArray: function(actual, message) {
        ok(actual.toString().match(/DS\.ManyArray/), message);
    }
});