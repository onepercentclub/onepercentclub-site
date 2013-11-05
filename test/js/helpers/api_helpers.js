// Mocking the API
function stubApiRequest(url, json) {
  $.mockjax({
    url: url,
    dataType: 'json',
    responseText: json
  });
}

var testTimeout;
module = function(name, mocks) {
  QUnit.module(name, {
    setup: function() {
      if (mocks) {
        if (mocks.setup) {
          mocks.setup.apply(this, arguments);
        }
        $.each(mocks, function(url, mock) {
          if (/setup|teardown/.test(url)) {
            return;
          }
          if ( $.type(mock) === "string" ){
            $.mockjax({
              url: "/api" + url,
              proxy: mock,
              responseTime: 1
            });
          } else {
            $.mockjax($.extend(mock,{url: "/api" + url}));
          }
        });
      }
      $.mockjax({
        url: "/api*",
        responseTime: 1,
        response: function(obj){
          var message = "Mockjax caught unmocked API call for url: " + obj.url
          if (obj.modelType) {
            message += ", from component " + obj.modelType;
          }
          ok( false, message );
        }
      });

      testTimeout = setTimeout(function() {
        equal( true, false, "test timeout (5s)" );
        // could involve multiple stop calls, reset
        QUnit.config.semaphore = 1;
        start();
      }, 5000);
    },
    
    teardown: function() {
      clearTimeout(testTimeout);
      $.mockjaxClear();
      if (mocks && mocks.teardown) {
        mocks.teardown.apply(this, arguments);
      }
    }
  });
};