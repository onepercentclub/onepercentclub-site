/*
  Add mixin to routes which require authentication
 */

App.TrackRouteActivateMixin = Ember.Mixin.create({
    activate: function() {
        this._super();

        Em.assert(this.toString() + ' must define tracker property', !Em.isEmpty(this.get('tracker')));
        Em.assert(this.toString() + ' must define trackEventName property', !Em.isEmpty(this.get('trackEventName')));

        this.get('tracker').trackEvent(this.get('trackEventName'));
    }
});