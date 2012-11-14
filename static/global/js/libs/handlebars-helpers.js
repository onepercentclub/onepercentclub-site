Handlebars.registerHelper('foreach', function(context, options) {
  var fn = options.fn, inverse = options.inverse;
  var ret = "";

  if(context && context.length > 0) {
    for(var i=0, j=context.length; i<j; i++) {
      var entry = context[i];
      entry.last = i == j-1;
      entry.first = i == 0;
      entry.index = i;
      ret = ret + fn(entry);
    }
  } else {
    ret = inverse(this);
  }
  console.log(ret);
  return ret;
});