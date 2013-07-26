
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
catalog['1-4 hours per month'] = '1-4 uur per maand';
catalog['1-4 hours per week'] = '1-4 uur per week';
catalog['5-8 hours per month'] = '5-8 uur per maand';
catalog['5-8 hours per week'] = '5-8 uur per week';
catalog['9-16 hours per month'] = '9-16 uur per maand';
catalog['9-16 hours per week'] = '9-16 uur per week';
catalog['Cancel'] = 'Annuleren';
catalog['Choose all'] = 'Kies allemaal';
catalog['Chosen %s'] = 'Gekozen %s';
catalog['Club / Association'] = 'Vereniging';
catalog['Company'] = 'Bedrijf';
catalog['Foundation'] = 'Stichting';
catalog['I have all the time in the world. Bring it on :D'] = 'Ik heb alle tijd van de wereld. Kom maar op!';
catalog['It depends on the content of the tasks. Challenge me!'] = 'Dat hangt van de taak af. Kom maar op met die uitdaging!';
catalog['Now'] = 'Nu';
catalog['Person'] = 'Persoon';
catalog['Remove all'] = 'Allemaal verwijderen';
catalog['School'] = 'School';


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

formats['DATETIME_FORMAT'] = 'j F Y H:i';
formats['DATE_FORMAT'] = 'j F Y';
formats['DECIMAL_SEPARATOR'] = ',';
formats['MONTH_DAY_FORMAT'] = 'j F';
formats['NUMBER_GROUPING'] = '3';
formats['TIME_FORMAT'] = 'H:i';
formats['FIRST_DAY_OF_WEEK'] = '1';
formats['TIME_INPUT_FORMATS'] = ['%H:%M:%S', '%H.%M:%S', '%H.%M', '%H:%M'];
formats['THOUSAND_SEPARATOR'] = '.';
formats['DATE_INPUT_FORMATS'] = ['%d-%m-%Y', '%d-%m-%y', '%Y-%m-%d'];
formats['YEAR_MONTH_FORMAT'] = 'F Y';
formats['SHORT_DATE_FORMAT'] = 'j-n-Y';
formats['SHORT_DATETIME_FORMAT'] = 'j-n-Y H:i';
formats['DATETIME_INPUT_FORMATS'] = ['%d-%m-%Y %H:%M:%S', '%d-%m-%y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H.%M:%S', '%d-%m-%y %H.%M:%S', '%d-%m-%Y %H:%M', '%d-%m-%y %H:%M', '%Y-%m-%d %H:%M', '%d-%m-%Y %H.%M', '%d-%m-%y %H.%M', '%d-%m-%Y', '%d-%m-%y', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S.%f'];

function get_format(format_type) {
    var value = formats[format_type];
    if (typeof(value) == 'undefined') {
      return format_type;
    } else {
      return value;
    }
}
