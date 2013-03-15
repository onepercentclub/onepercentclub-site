/**
 * {{localize SomeNumber}} -> 123
 * {{localize SomeNumber "n2"}} -> 123.45
 * https://github.com/jquery/globalize#numbers
 *
 * {{localize SomeDate "D"}} -> Monday, February 20, 2012
 * {{localize SomeDate "MM,YY"}} -> 02, 12
 *
 */
Handlebars.registerHelper('localize', function (value, formatting) {
    // Check if it's a Ember Data number or a date
    var value = this.get(value);
    // If there's no second argument then formatting will be an object. Set it to null instead.
    var formatting = (typeof formatting == 'string') ? formatting : null;
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
