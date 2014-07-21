
/* gettext library */

var catalog = new Array();

function pluralidx(n) {
  var v=(n != 1);
  if (typeof(v) == 'boolean') {
    return v ? 1 : 0;
  } else {
    return v;
  }
}
catalog['15 minutes'] = '15 minutes';
catalog['Apply for task'] = 'Apply for task';
catalog['Apply'] = 'Apply';
catalog['Are you sure you want to delete this comment?'] = 'Are you sure you want to delete this comment?';
catalog['Are you sure you want to delete this reaction?'] = 'Are you sure you want to delete this reaction?';
catalog['Cancel'] = 'Cancel';
catalog['Club / Association'] = 'Club / Association';
catalog['Company'] = 'Company';
catalog['Deadline<br /> reached'] = 'Deadline<br /> reached';
catalog['Email address'] = 'Email address';
catalog['Emails don\'t match'] = 'Whoops! The email addresses don\'t match.';
catalog['Error saving model.'] = 'Error saving model.';
catalog['Failed to create currentUser'] = 'Whoops... Something went wrong. We\'re going to fix this asap!';
catalog['First name'] = 'First name';
catalog['Foundation'] = 'Foundation';
catalog['Hey! What are you doing here? Saving model failed.'] = 'Hey! What are you doing here? Saving model failed.';
catalog['Instance does not implement `_save`.'] = 'Instance does not implement `_save`.';
catalog['Invalid email address'] = 'Oh no! This is an invalid email address.';
catalog['Model could not be saved.'] = 'Model could not be saved.';
catalog['Model is invalid.'] = 'Model is invalid.';
catalog['Model is not dirty.'] = 'Model is not dirty.';
catalog['Model saved successfully.'] = 'Model saved successfully.';
catalog['No, continue'] = 'No, continue';
catalog['Password needs to be at least 6 characters long'] = 'Password needs to be at least 6 characters long.';
catalog['Password required'] = 'Please fill in your password.';
catalog['Password'] = 'Password';
catalog['Person'] = 'Persoon';
catalog['Pick a country'] = 'Pick a country';
catalog['Pick a phase'] = 'Pick a phase';
catalog['Pick an item'] = 'Pick an item';
catalog['Pick an organization'] = 'Pick an organisation';
catalog['Re-enter email address'] = 'Re-enter email address';
catalog['Really?'] = 'Really?';
catalog['Save changed data?'] = 'Save changed data?';
catalog['Save'] = 'Save';
catalog['Saving'] = 'Saving';
catalog['School'] = 'School';
catalog['Set my monthly donation'] = 'Set my monthly donation';
catalog['Stop my monthly donation'] = 'Stop my monthly donation';
catalog['Successfully saved.'] = 'Successfully saved.';
catalog['Surname can\'t be left empty'] = 'Last name can\'t be left empty';
catalog['Surname'] = 'Last name';
catalog['Thanks a lot for your support until now. You rock! We welcome you back anytime.<br /><br />Are you sure you want to stop your monthly support?'] = 'Thanks a lot for your support until now. You rock! We welcome you back anytime.<br /><br />Are you sure you want to stop your monthly donation?';
catalog['There was an error connecting Facebook'] = 'Oh snap! There was an error connecting with your Facebook account. Please try again.';
catalog['There was an error with your payment. Please try again.'] = 'There was an error with your payment. Could you please try again?';
catalog['Unauthorized to connect to Facebook '] = 'We\'re unauthorized to connect to your Facebook account.';
catalog['We\'ve sent a password reset link to your inbox'] = 'We\'ve sent a password reset link to your inbox. See you at onepercentclub.com in a minute!';
catalog['Yes'] = 'Yes';
catalog['Yes, stop my donation'] = 'Yes, stop my donation';
catalog['You have some unsaved changes. Do you want to save before you leave?'] = 'You have some unsaved changes. Do you want to save before you leave?';
catalog['You\'re about to set a monthly donation.<br/><br/>'] = 'You\'re about to set a monthly donation.<br/><br/>';
catalog['by'] = 'by';
catalog['day'] = 'day';
catalog['days'] = 'days';
catalog['fair'] = 'fair';
catalog['half a day'] = 'half a day';
catalog['half an hour'] = '30 minutes';
catalog['of'] = 'of';
catalog['one day'] = 'one day';
catalog['one month'] = 'one month';
catalog['one week'] = 'one week';
catalog['raised'] = 'raised';
catalog['strong'] = 'strong';
catalog['to support this project'] = 'to support this campaign';
catalog['two days'] = 'two days';
catalog['two hours'] = 'two hours';
catalog['two weeks'] = 'two weeks';
catalog['up to one hour'] = 'up to one hour';
catalog['weak'] = 'weak';


function gettext(msgid) {
  var value = catalog[msgid];
  if (typeof(value) == 'undefined') {
    return msgid;
  } else {
    return (typeof(value) == 'string') ? value : value[0];
  }
}

function ngettext(singular, plural, count) {
  value = catalog[singular];
  if (typeof(value) == 'undefined') {
    return (count == 1) ? singular : plural;
  } else {
    return value[pluralidx(count)];
  }
}

function gettext_noop(msgid) { return msgid; }

function pgettext(context, msgid) {
  var value = gettext(context + '\x04' + msgid);
  if (value.indexOf('\x04') != -1) {
    value = msgid;
  }
  return value;
}

function npgettext(context, singular, plural, count) {
  var value = ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
  if (value.indexOf('\x04') != -1) {
    value = ngettext(singular, plural, count);
  }
  return value;
}

function interpolate(fmt, obj, named) {
  if (named) {
    return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
  } else {
    return fmt.replace(/%s/g, function(match){return String(obj.shift())});
  }
}

/* formatting library */

var formats = new Array();

formats['DATETIME_FORMAT'] = 'N j, Y, P';
formats['DATE_FORMAT'] = 'N j, Y';
formats['DECIMAL_SEPARATOR'] = '.';
formats['MONTH_DAY_FORMAT'] = 'F j';
formats['NUMBER_GROUPING'] = '3';
formats['TIME_FORMAT'] = 'P';
formats['FIRST_DAY_OF_WEEK'] = '0';
formats['TIME_INPUT_FORMATS'] = ['%H:%M:%S', '%H:%M'];
formats['THOUSAND_SEPARATOR'] = ',';
formats['DATE_INPUT_FORMATS'] = ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'];
formats['YEAR_MONTH_FORMAT'] = 'F Y';
formats['SHORT_DATE_FORMAT'] = 'm/d/Y';
formats['SHORT_DATETIME_FORMAT'] = 'm/d/Y P';
formats['DATETIME_INPUT_FORMATS'] = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M', '%m/%d/%Y', '%m/%d/%y %H:%M:%S', '%m/%d/%y %H:%M', '%m/%d/%y', '%Y-%m-%d %H:%M:%S.%f'];

function get_format(format_type) {
    var value = formats[format_type];
    if (typeof(value) == 'undefined') {
      return format_type;
    } else {
      return value;
    }
}
