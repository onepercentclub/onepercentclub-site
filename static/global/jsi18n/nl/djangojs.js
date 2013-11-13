
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
catalog['%(sel)s of %(cnt)s selected'] = ['',''];
catalog['%(sel)s of %(cnt)s selected'][0] = '%(sel)s of %(cnt)s selected';
catalog['%(sel)s of %(cnt)s selected'][1] = '%(sel)s of %(cnt)s geselecteerd';
catalog['--loading--'] = '--laadt--';
catalog['1-4 hours per month'] = '1-4 uur per maand';
catalog['1-4 hours per week'] = '1-4 uur per week';
catalog['15 minutes'] = 'een kwartier';
catalog['5-8 hours per month'] = '5-8 uur per maand';
catalog['5-8 hours per week'] = '5-8 uur per week';
catalog['6 a.m.'] = '6 uur';
catalog['9-16 hours per month'] = '9-16 uur per maand';
catalog['9-16 hours per week'] = '9-16 uur per week';
catalog['Act'] = 'Uitvoering';
catalog['Apply'] = 'Aanmelden';
catalog['Are you sure you want to apply to this task?'] = 'Weet je zeker dat je je wilt aanmelden voor deze taak?';
catalog['Are you sure you want to delete this comment?'] = 'Wil je dit bericht echt verwijderen?';
catalog['Are you sure you want to delete this reaction?'] = 'Wil je deze reactie echt verwijderen?';
catalog['Available %s'] = 'Beschikbaar %s';
catalog['Calendar'] = 'Kalender';
catalog['Campaign'] = 'Campagne';
catalog['Cancel'] = 'Annuleren';
catalog['Choose a time'] = 'Kies een tijd';
catalog['Choose all'] = 'Kies allemaal';
catalog['Choose'] = 'Kies';
catalog['Chosen %s'] = 'Gekozen %s';
catalog['Click to choose all %s at once.'] = 'Klik om alle %s tegelijk te selecteren.';
catalog['Click to remove all chosen %s at once.'] = 'Klik om alle %s tegelijk te verwijderen.';
catalog['Clock'] = 'Uur';
catalog['Club / Association'] = 'Vereniging';
catalog['Company'] = 'Bedrijf';
catalog['Filter'] = 'Kies';
catalog['Foundation'] = 'Stichting';
catalog['Hide'] = 'Verberg';
catalog['I have all the time in the world. Bring it on!'] = 'Tijd genoeg, kom maar op!';
catalog['It depends on the content of the tasks. Challenge me!'] = 'Dat hangt van de taak af. Kom maar op met die uitdaging!';
catalog['January February March April May June July August September October November December'] = 'januari februari maart april mei juni juli augustus september oktober november december';
catalog['Midnight'] = 'Middernacht';
catalog['Noon'] = '12 uur';
catalog['Now'] = 'Nu';
catalog['Person'] = 'Persoon';
catalog['Pick a country'] = 'Kies land';
catalog['Pick a phase'] = 'Kies een fase';
catalog['Please use your email address to log in.'] = 'Gebruik je e-mailadres om in te loggen';
catalog['Realised'] = 'Gerealiseerd';
catalog['Really?'] = 'Zeker weten?';
catalog['Remove all'] = 'Allemaal verwijderen';
catalog['Remove'] = 'Verwijder';
catalog['Results'] = 'Resultaten';
catalog['S M T W T F S'] = 'Z M D W D V Z';
catalog['Save changed data?'] = 'Wijzigingen opslaan?';
catalog['Save'] = 'Opslaan';
catalog['Saving'] = 'Slaat op';
catalog['School'] = 'School';
catalog['Show'] = 'Bekijk';
catalog['Task'] = 'Taak';
catalog['The token you provided is expired. Please reset your password again.'] = 'De code die je opgeeft is verlopen. Stel je wachtwoord opnieuw in. ';
catalog['This is the list of available %s. You may choose some by selecting them in the box below and then clicking the "Choose" arrow between the two boxes.'] = 'Dit is de lijst van beschikbare %s. Je kan kiezen door ze te selecteren in het vakje en dan op de "Kies" pijl tussen de twee vakjes te klikken.';
catalog['This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the "Remove" arrow between the two boxes.'] = 'Dit is de lijst van gekozen %s. Je kan verwijderen door ze te selecteren in het vakje en dan op de "Verwijder" pijl tussen de twee vakjes te klikken.';
catalog['Today'] = 'Vandaag';
catalog['Tomorrow'] = 'Morgen';
catalog['Type into this box to filter down the list of available %s.'] = 'Typ in het vakje om de lijst van beschikbare %s te zien.';
catalog['Writing Plan'] = 'Plan';
catalog['YOU\'VE GOT MAIL!<br /><br />We\'ve sent you a link to reset your password, so check your mailbox.<br /><br />(No mail? It might have ended up in your spam folder)'] = 'YOU\'VE GOT MAIL!<br /><br />We hebben je een link gestuurd om je wachtwoord te wijzigen.<br /><br />(Geen email? Kijk dan even in je spam folder)';
catalog['Yes'] = 'Ja';
catalog['Yesterday'] = 'Gisteren';
catalog['You have selected an action, and you haven\'t made any changes on individual fields. You\'re probably looking for the Go button rather than the Save button.'] = 'Je hebt een actie geselecteerd, en je hebt geen wijzigingen uitgevoerd. Je zoekt waarschijnlijk de GO knop in plaats van de Save knop. ';
catalog['You have selected an action, but you haven\'t saved your changes to individual fields yet. Please click OK to save. You\'ll need to re-run the action.'] = 'Je hebt een actie geselecteerd, maar je hebt je wijzigingen nog niet opgeslagen. Klik op Ok om op te slaan. Je moet de actie opnieuw uitvoeren. ';
catalog['You have some unsaved changes. Do you want to save before you leave?'] = 'Je hebt niet-opgeslagen wijzigingen. Wil je deze eerst opslaan?';
catalog['You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.'] = 'Je hebt wijzigingen niet opgeslagen. Als je een actie uitvoert, dan gaan je niet opgeslagen wijzigingen verloren.';
catalog['half a day'] = 'een halve dag';
catalog['half an hour'] = 'een half uur';
catalog['one day'] = 'een dag';
catalog['one month'] = 'een maand';
catalog['one week'] = 'een week';
catalog['two days'] = 'twee dagen';
catalog['two hours'] = 'twee uur';
catalog['two weeks'] = 'twee weken';
catalog['up to one hour'] = 'een uur';


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
