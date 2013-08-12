/**
 * {{localize SomeNumber}} -> 123
 * {{localize SomeNumber "n2"}} -> 123.45
 * https://github.com/jquery/globalize#numbers
 *
 * {{localize SomeDate "D"}} -> Monday, February 20, 2012
 * {{localize SomeDate "MM,YY"}} -> 02, 12
 *
 */
Em.Handlebars.registerBoundHelper('localize', function (value, options) {
    // Unfortunately although this is 'bound' it won't update it since the value doesn't change.

    // If there's no second argument then formatting will be an object. Set it to null instead.
    var formatting = options.hash['formatting'];
    // Check if it's a Ember Data number or a date
    if (Ember.typeOf(value) == 'number') {
        if (!formatting) {
            formatting = 'n0';
        }
        return new Handlebars.SafeString(Globalize.format(value, formatting));
    }
    if (Ember.typeOf(value) == 'date') {
        if (!formatting) {
            formatting = 'd';
        }
        return new Handlebars.SafeString(Globalize.format(value, formatting));
    }
    return new Handlebars.SafeString(Globalize.format(value));
});

Em.Handlebars.registerBoundHelper('linebreaks', function(value, options) {
    if(!value) return ''

    var formatting = options.hash['formatting'];
    if (!formatting || formatting == 'br') {
        return new Handlebars.SafeString(value.replace(/\n\r?/g, '<br />'));
    }
    else {
        return new Handlebars.SafeString('<p>' + value.replace(/\n\r?/g, '</p><p>') + '</p>');
    }
});

