from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import truncate_words
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from sorl.thumbnail import ImageField
from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager
from apps.bluebottle_utils.fields import MoneyField
from apps.fund.models import Donation


class ProjectTheme(models.Model):
    """ Themes for Projects. """

    # The name is marked as unique so that users can't create duplicate theme names.
    name = models.CharField(_("name"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)
    description = models.TextField(_("description"), blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("project theme")
        verbose_name_plural = _("project themes")


class Project(models.Model):
    """ The base Project model. """

    class ProjectPhases(DjangoChoices):
        idea = ChoiceItem('idea', label=_("Idea"))
        fund = ChoiceItem('fund', label=_("Fund"))
        act = ChoiceItem('act', label=_("Act"))
        results = ChoiceItem('results', label=_("Results"))

    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)

    partner_organization = models.ForeignKey('PartnerOrganization', blank=True, null=True, verbose_name=_('partner organization'))
    image = ImageField(_("image"), max_length=255, blank=True, upload_to='project_images/', help_text=_("Main project picture"))
    organization = models.ForeignKey('organizations.Organization', verbose_name=_("organization"))
    owner = models.ForeignKey('auth.User', verbose_name=_("owner"))
    phase = models.CharField(_("phase"), max_length=20, choices=ProjectPhases.choices, help_text=_("Phase this project is in right now."))
    themes = models.ManyToManyField(ProjectTheme, blank=True, verbose_name=_("themes"))
    created = CreationDateTimeField(_("created"), help_text=_("When this project was created."))

    # Location of this project
    # Normally, 7 digits and 4 decimal places should suffice, but it wouldn't
    # hold the legacy data.
    # http://stackoverflow.com/questions/7167604/how-accurately-should-i-store-latitude-and-longitude
    latitude = models.DecimalField(_("latitude"), max_digits=21, decimal_places=18)
    longitude = models.DecimalField(_("longitude"), max_digits=21, decimal_places=18)
    country = models.ForeignKey('geo.Country', blank=True, null=True, verbose_name=_("country"))

    language = models.CharField(max_length=6, choices=settings.LANGUAGES, help_text=_("Main language of the project."))
    tags = TaggableManager(blank=True, verbose_name=_("tags"))

    planned_start_date = models.DateField(_("planned start date"), blank=True, null=True,
        help_text=_("The project owner's notion of the project start date. "
                    "This date is independent of the various phase start dates.")
    )
    planned_end_date = models.DateField(_("planned end date"), blank=True, null=True,
        help_text=_("The project owner's notion of the project end date. "
                    "This date is independent of the various phase end dates.")
    )

    def __unicode__(self):
        if self.title:
            return self.title
        return self.slug

    # This is here to provide a consistent way to get money_asked.
    @property
    def money_asked(self):
        try:
            self.fundphase
        except FundPhase.DoesNotExist:
            return Decimal('0.00')
        return self.fundphase.money_asked

    # This is here to provide a consistent way to get money_donated.
    @property
    def money_donated(self):
        if self.money_asked == Decimal('0.00'):
            return Decimal('0.00')
        try:
            return self.fundphase.money_donated
        except FundPhase.DoesNotExist:
            return Decimal('0.00')

    @models.permalink
    def get_absolute_url(self):
        """ Get the URL for the current project. """
        return 'project-detail', (), {'slug': self.slug}

    @property
    def description(self):
        # TODO We need to figure out the best spot for description once the interaction design is worked.
        try:
            return self.fundphase.description
        except FundPhase.DoesNotExist:
            try:
                return self.ideaphase.description
            except IdeaPhase.DoesNotExist:
                return ""

    class Meta:
        ordering = ['title']
        verbose_name = _("project")
        verbose_name_plural = _("projects")


class PartnerOrganization(models.Model):
    """
        Some projects are run in cooperation with a partner
        organization like EarthCharter & MacroMicro
    """
    name = models.CharField(_("name"), max_length=255, unique=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("partner organization")
        verbose_name_plural = _("partner organizations")

    def __unicode__(self):
        if self.name:
            return self.name
        return self.slug


class AbstractPhase(models.Model):
    """ Abstract base class for project phases. """

    class PhaseStatuses(DjangoChoices):
        hidden = ChoiceItem('hidden', label=_("Hidden"))
        progress = ChoiceItem('progress', label=_("Progress"))
        waiting = ChoiceItem('waiting', label=_("Waiting"))
        completed = ChoiceItem('completed', label=_("Completed"))

    project = models.OneToOneField(Project, verbose_name=_("project"))
    title = models.CharField(_("title"), max_length=255, blank=True)
    description = models.TextField(_("description"), blank=True)

    # Date the phase has started/ended.
    startdate = models.DateField(_("start date"))
    enddate = models.DateField(_("end date"), blank=True, null=True)

    status = models.CharField(_("status"), max_length=20, choices=PhaseStatuses.choices)

    def clean(self):
        if self.startdate and self.enddate:
            if self.enddate < self.startdate:
                raise ValidationError(_(
                    u"%(classname)s: End date %(enddate)s can not be earlier than start date %(startdate)s" %
                    {'classname': self.__class__.__name__, 'enddate': self.enddate, 'startdate': self.startdate})
                )

    def save(self, *args, **kwargs):
        self.clean()
        super(AbstractPhase, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class IdeaPhase(AbstractPhase):
    """ IdeaPhase: Got a nice idea here. """

    knowledge_description = models.TextField(_("knowledge"), blank=True, help_text=_("Description of knowledge."))

    class Meta:
        verbose_name = _("idea phase")
        verbose_name_plural = _("idea phase")


class FundPhase(AbstractPhase):
    """ FundPhase: Fill out some forms for project plan. """

    class PhaseStatuses(DjangoChoices):
        hidden = ChoiceItem('hidden', label=_("Hidden"))
        progress = ChoiceItem('progress', label=_("Progress"))
        feedback = ChoiceItem('feedback', label=_("Feedback"))
        waiting = ChoiceItem('waiting', label=_("Waiting"))
        completed = ChoiceItem('completed', label=_("Completed"))

    class ImpactGroups(DjangoChoices):
        children = ChoiceItem('children', label=_("Children"))
        youth = ChoiceItem('youth', label=_("Youth"))
        adults = ChoiceItem('adults', label=_("Adults"))

    description_long = models.TextField(
        _("description"), blank=True, help_text=_("Longer description.")
    )

    budget_total = MoneyField(_("budget total"), help_text=_("Amount of money needed for a project including money from other sources."))
    money_asked = MoneyField(_("money asked"), help_text=_("Amount of money asked for a project from this website."))
    money_donated= MoneyField(_('money donated'), help_text=_("This field is updated on every donation(change)"))

    sustainability = models.TextField(_("sustainability"), blank=True,help_text=_("How can next generations profit from this?"))
    money_other_sources = models.TextField(_("money from other sources"), blank=True, help_text=_("Money received from other sources."))

    # Social Impact: who are we helping, direct and indirect
    social_impact = models.TextField(_("social impact"), blank=True,help_text=_("Who are you helping?"))
    impact_group = models.CharField(_("impact group"), max_length=20, choices=ImpactGroups.choices, blank=True)
    impact_direct_male = models.IntegerField(_("impact direct male"), max_length=6, default=0)
    impact_direct_female = models.IntegerField(_("impact direct female"), max_length=6, default=0)
    impact_indirect_male = models.IntegerField(_("impact indirect male"),max_length=6, default=0)
    impact_indirect_female = models.IntegerField(_("impact indirect female"), max_length=6, default=0)

    # This updates the 'cached' donated amount. This should be run everytime a
    # donation is made or changes status.
    # TODO: Add out of band integrity checks (e.g. as a separate cron task)
    def update_money_donated(self):
        donations = Donation.objects.filter(project=self.project)
        donations = donations.filter(status__in=['closed','paid','started'])
        total = donations.aggregate(total=Sum('amount'))['total']
        if total is None:
            if self.money_donated != 0:
                # Only set money_donated to 0 when it's not already 0.
                self.money_donated = 0
                self.save()
        elif self.money_donated != total:
            self.money_donated = total
            self.save()
        return self.money_donated


    class Meta:
        verbose_name = _("fund phase")
        verbose_name_plural = _("fund phase")


class ActPhase(AbstractPhase):
    """ ActPhase Funding complete. Let's DO it! """

    planning = models.TextField(_("planning"), blank=True)

    class Meta:
        verbose_name = _("act phase")
        verbose_name_plural = _("act phase")


class ResultsPhase(AbstractPhase):
    """ ResultsPhase: Tell about how things worked out. """

    # Five questions that get asked after the project is done.
    what = models.TextField(_("what"), help_text=_("What and how?"), blank=True)
    tips = models.TextField(_("tips"), help_text=_("Tips and tricks?"), blank=True)
    change = models.TextField(_("change"), help_text=_("What has changed for the target group?"), blank=True)
    financial = models.TextField(_("financial"), help_text=_("How was the money spend?"), blank=True)
    next = models.TextField(_("next"), help_text=_("What's next?"), blank=True)

    class Meta:
        verbose_name = _("results phase")
        verbose_name_plural = _("results phase")


# TODO: What is the for? Is is supposed to be reference? How is it related to Projects?
class Referral(models.Model):
    """
    People that are named as a referral.
    """
    name = models.CharField(_("name"), max_length=255)
    email = models.EmailField(_("email"))
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = _("referral")
        verbose_name_plural = _("referrals")


class BudgetLine(models.Model):
    """
    BudgetLine: Entries to the Project Budget sheet.
    This is the budget for the amount asked from this
    website.
    """
    project = models.ForeignKey(Project, verbose_name=_("project"))
    description = models.CharField(_("description"), max_length=255)
    money_amount = MoneyField(_("money amount"))

    class Meta:
        verbose_name = _("budget line")
        verbose_name_plural = _("budget lines")


# Now some stuff connected to Projects
# FIXME: Can we think of a better place to put this??
class Link(models.Model):
    """ Links (URLs) connected to a Project. """

    project = models.ForeignKey(Project, verbose_name=_("project"))
    name = models.CharField(_("name"), max_length=255)
    url = models.URLField(_("URL"))
    description = models.TextField(_("description"), blank=True)
    ordering = models.IntegerField(_("ordering"))
    created = CreationDateTimeField(_("created"))

    class Meta:
        ordering = ['ordering']
        verbose_name = _("link")
        verbose_name_plural = _("links")


class Testimonial(models.Model):
    """ Any user can write something nice about a project. """

    project = models.ForeignKey(Project, verbose_name=_("project"))
    user = models.ForeignKey('auth.User', verbose_name=_("user"))
    description = models.TextField(_("description"))
    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    class Meta:
        ordering = ['-created']
        verbose_name = _("testimonial")
        verbose_name_plural = _("testimonials")

    def __unicode__(self):
        return truncate_words(self.description, 20)


#
# The Phase start / end date synchronization logic.
#
def set_previous_phase_enddate(current_phase, previous_phase):
    """
    Sets the enddate of the previous phase to the startdate of the current phase.
    """

    if previous_phase.enddate != current_phase.startdate:
        previous_phase.enddate = current_phase.startdate
        if previous_phase.enddate < previous_phase.startdate:
            previous_phase.startdate = previous_phase.enddate
        # TODO In Django 1.5 this can be changed to only save the 'enddate' field:
        # https://docs.djangoproject.com/en/dev/ref/models/instances/#specifying-which-fields-to-save
        previous_phase.save()

def set_next_phase_startdate(current_phase, next_phase):
    """
    Sets the startdate of the next phase to the enddate of the current phase.
    """

    if next_phase.startdate != current_phase.enddate:
        next_phase.startdate = current_phase.enddate
        if next_phase.enddate is not None and next_phase.startdate > next_phase.enddate:
            next_phase.enddate = next_phase.startdate
        # TODO In Django 1.5 this can be changed to only save the 'startdate' field:
        # https://docs.djangoproject.com/en/dev/ref/models/instances/#specifying-which-fields-to-save
        next_phase.save()

@receiver(post_save, weak=False, sender=IdeaPhase)
def sync_idea_phase_dates(sender, instance, created, **kwargs):
    try:
        set_next_phase_startdate(instance, instance.project.fundphase)
    except FundPhase.DoesNotExist:
        pass

@receiver(post_save, weak=False, sender=FundPhase)
def sync_fund_phase_dates(sender, instance, created, **kwargs):
    try:
        set_previous_phase_enddate(instance, instance.project.ideaphase)
    except IdeaPhase.DoesNotExist:
        pass

    try:
        set_next_phase_startdate(instance, instance.project.actphase)
    except ActPhase.DoesNotExist:
        pass

@receiver(post_save, weak=False, sender=ActPhase)
def sync_act_phase_dates(sender, instance, created, **kwargs):
    try:
        set_previous_phase_enddate(instance, instance.project.fundphase)
    except FundPhase.DoesNotExist:
        pass

    try:
        set_next_phase_startdate(instance, instance.project.resultsphase)
    except ResultsPhase.DoesNotExist:
        pass

@receiver(post_save, weak=False, sender=ResultsPhase)
def sync_results_phase_dates(sender, instance, created, **kwargs):
    try:
        set_previous_phase_enddate(instance, instance.project.actphase)
    except ActPhase.DoesNotExist:
        pass
