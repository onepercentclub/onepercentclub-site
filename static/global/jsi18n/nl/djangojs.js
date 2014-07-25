
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
catalog['<h3>Introduction of your campaign</h3><p>We\u2019ve already set some structure in this plan, but you are free to write it in your own way.</p><h3>What are you going to do?</h3><p>Remember to keep a logic structure, use headings, paragraphs.</p><h3>How are you going to achieve that?</h3><p>Keep it short and sweet!</p>'] = '<p>Met eigen headers en wit regels kun je hier je campagne verhaal uitleggen, bijvoorbeeld door middel van een:</p>\u00a0\n<h3>Introductie</h3>\u00a0\n<p>Leg uit waar je campagne voor is, vertel iets over bijvoorbeeld het doel van de campagne. Supporters zullen ook benieuwd zijn waar het geld precies voor gebruikt gaat worden.</p>\n<h3>Waarom</h3>\n<p>Licht eventueel de grote waarom vragen toe: waarom is deze campagne zo belangrijk? waarom zouden mensen deze campagne moeten supporten?\nWe laten je helemaal vrij in het schrijven van je verhaal. Eventueel kun je hier ook nog informatie later aan toevoegen of aanpassen. Let wel op dat je dit niet te veel doet, je verhaal moet altijd concreet, urgent en persoonlijk blijven.<p>';
catalog['Cancel'] = 'Annuleer';
catalog['Finished campaigns'] = 'Afgeronde campagnes';
catalog['No, continue'] = 'Nee, ga verder';
catalog['Running campaigns'] = 'Openstaande campagnes';
catalog['Save changed data?'] = 'Wijzigingen opslaan?';
catalog['Save'] = 'Opslaan';
catalog['Set my monthly donation'] = 'Stel maandelijkse donatie in';
catalog['Stop my monthly donation'] = 'Stop maandelijkse donatie';
catalog['Thanks a lot for your support until now. You rock! We welcome you back anytime.<br /><br />Are you sure you want to stop your monthly support?'] = 'Bedankt voor je support tot dusver. Super! Uiteraard, je kunt altijd weer je maandelijkse donatie activeren.<br /><br />Weet je zeker dat je je maandelijkse donatie wilt stopzetten?';
catalog['There was an error connecting Facebook'] = 'Oeps! We konden geen verbinding maken met je Facebook account. Probeer het nog eens.';
catalog['There was an error with your payment. Please try again.'] = 'Er ging iets mis met de betaling. Kun je het nogmaals proberen?';
catalog['Welcome!'] = 'Welkom!';
catalog['Yes, stop my donation'] = 'Ja, stop donatie';
catalog['You have some unsaved changes. Do you want to save before you leave?'] = 'Je hebt niet-opgeslagen wijzigingen. Wil je deze eerst opslaan?';
catalog['You\'re about to set a monthly donation.<br/><br/>'] = 'Super! Je gaat maandelijks doneren.';
catalog['by'] = 'door';
catalog['of'] = 'van';
catalog['raised'] = 'opgehaald';


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
