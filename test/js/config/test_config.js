document.write('<div id="ember-testing-container"><div id="ember-testing"></div></div>');

App.Store = DS.Store.extend({
  adapter: DS.FixtureAdapter.extend({})
});

App.rootElement = '#ember-testing';

App.setupForTesting();
// App.injectTestHelpers();
Ember.run(App, App.advanceReadiness);

function exists(selector) {
  return !!find(selector).length;
}

function getAssertionMessage(actual, expected, message) {
  return message || QUnit.jsDump.parse(expected) + " expected but was " + QUnit.jsDump.parse(actual);
}

function equal(actual, expected, message) {
  message = getAssertionMessage(actual, expected, message);
  QUnit.equal.call(this, actual, expected, message);
}

function strictEqual(actual, expected, message) {
  message = getAssertionMessage(actual, expected, message);
  QUnit.strictEqual.call(this, actual, expected, message);
}

window.exists = exists;
window.equal = equal;
window.strictEqual = strictEqual;