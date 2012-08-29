from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth.models import User
import random

from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField
)
from djchoices import DjangoChoices, ChoiceItem
from sorl.thumbnail import ImageField
from taggit.managers import TaggableManager

from apps.bluebottle_utils.fields import MoneyField


class ProjectTheme(models.Model):
    """ Themes for Projects. """

    # The name is marked as unique so that users can't create duplicate
    # theme names.
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

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

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)

    partner_organization = models.ForeignKey('PartnerOrganization', blank=True, null=True)

    image = ImageField(max_length=255, blank=True,
        upload_to='project_images/',
        help_text=_("Main project picture"))

    organization = models.ForeignKey('organizations.Organization')
    owner = models.ForeignKey('auth.User')
    phase = models.CharField(max_length=20, choices=ProjectPhases.choices,
        help_text=_("Phase this project is in right now."))
    themes = models.ManyToManyField(ProjectTheme, blank=True)
    created = CreationDateTimeField(
        help_text=_("When this project was created."))

    # Location of this project
    # Normally, 7 digits and 4 decimal places should suffice, but it wouldn't
    # hold the legacy data.
    # Ref http://stackoverflow.com/questions/7167604/how-accurately-should-i-store-latitude-and-longitude
    latitude = models.DecimalField(max_digits=21, decimal_places=18)
    longitude = models.DecimalField(max_digits=21, decimal_places=18)
    country = models.ForeignKey('geo.Country', blank=True, null=True)

    project_language = models.CharField(max_length=6,
        choices=settings.LANGUAGES,
        help_text=_("Main language of the project."))

    albums = models.ManyToManyField('media.Album', blank=True, null=True)

    tags = TaggableManager(blank=True)

    # temporary to do hold random 'donated'
    donated = 0

    def __unicode__(self):
        if self.title:
            return self.title
        return self.slug


    def money_asked(self):
        return int(self.fundphase.money_asked)

    """ Money donated, rounded to the lower end... """
    # Money donated. For now this is random
    # TODO: connect this to actual donations. Duh!
    def money_donated(self):
        if self.donated == 0:
            self.donated = int(random.randrange(5, self.money_asked()))
        return int(self.donated)

    def money_needed(self):
        return self.money_asked() - self.money_donated()

    @models.permalink
    def get_absolute_url(self):
        """ Get the URL for the current project. """

        return ('project_detail', (), {
            'slug': self.slug
        })

    def get_supporters(self):
        """ Get a queryset of donating users for this project. """

        # TODO: Add filter for 'succesful' donations on a somewhat higher
        # level, perhaps a custom Manager on Donation/DonationLine classes.
        donators = User.objects
        donators = donators.filter(donation__donationline__project=self)
        donators = donators.filter(donation__status__in=['closed','paid','started'])
        donators = donators.distinct()
        return donators

    class Meta:
        ordering = ['title']
        verbose_name = _("project")
        verbose_name_plural = _("projects")


class PartnerOrganization(models.Model):
    """ 
        Some projects are run in cooperation with a partner 
        organization like EarthCharter & MacroMicro
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

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
        completed = ChoiceItem('completed', label=_("Completed"))

    project = models.OneToOneField(Project)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    # Date the phase has started/ended.
    startdate = models.DateField(null=True)
    enddate = models.DateField(null=True)

    status = models.CharField(max_length=20, choices=PhaseStatuses.choices)

    class Meta:
        abstract = True


class IdeaPhase(AbstractPhase):
    """ IdeaPhase: Got a nice idea here. """
    knowledge_description = models.TextField(blank=True)

    class Meta:
        verbose_name = _("idea phase")
        verbose_name_plural = _("idea phases")


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

    description_long = models.TextField(blank=True)

    budget_total = MoneyField(_('money total'),
        help_text=_("Total amount needed for this project."))
    money_asked = MoneyField(_('money asked'),
        help_text=_("Amount asked for from this website."))

    sustainability = models.TextField(
        blank=True,
        help_text=_("How can next generations profit from this?"))

    money_other_sources = models.TextField(blank=True)

    """ Social Impact: who are we helping, direct and indirect """
    social_impact = models.TextField(
        blank=True,
        help_text=_("Who are you helping?"))
    impact_group = models.CharField(max_length=20, choices=ImpactGroups.choices, blank=True)
    impact_direct_male = models.IntegerField(max_length=6, default=0)
    impact_direct_female = models.IntegerField(max_length=6, default=0)
    impact_indirect_male = models.IntegerField(max_length=6, default=0)
    impact_indirect_female = models.IntegerField(max_length=6, default=0)

    class Meta:
        verbose_name = _("fund phase")
        verbose_name_plural = _("fund phases")


class ActPhase(AbstractPhase):
    """ ActPhase Funding complete. Let's DO it! """

    planning = models.TextField(blank=True)
    planned_start_date = models.DateField(null=True)
    planned_end_date = models.DateField(null=True)

    class Meta:
        verbose_name = _("act phase")
        verbose_name_plural = _("act phases")


class ResultsPhase(AbstractPhase):
    """ ResultsPhase: Tell about how things worked out. """

    # Five questions that get asked after the project is done.
    what = models.TextField(
        help_text=_("What and how?"),
        blank=True)
    tips = models.TextField(
        help_text=_("Tips and tricks?"),
        blank=True)
    change = models.TextField(
        help_text=_("What has changed for the target group?"),
        blank=True)
    financial = models.TextField(
        help_text=_("How was the money spend?"),
        blank=True)
    next = models.TextField(
        help_text=_("What's next?"),
        blank=True)

    class Meta:
        verbose_name = _("results phase")
        verbose_name_plural = _("results phases")


class Referals(models.Model):
    """
    People that are named as referals.
    
    TODO: Fix spelling error and make singular.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField()
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _("referral")
        verbose_name_plural = _("referrals")


class BudgetLine(models.Model):
    """
    BudgetLine: Entries to the Project Budget sheet.
    This is the budget for the amount asked from this
    website.
    """
    project = models.ForeignKey(Project)
    description = models.TextField(blank=True)
    money_amount = MoneyField()

    class Meta:
        verbose_name = _("budget line")
        verbose_name_plural = _("budget lines")


# Now some stuff connected to Projects
# FIXME: Can we think of a better place to put this??
class Link(models.Model):
    """ Links (URLs) connected to a Project. """

    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(blank=True)
    ordering = models.IntegerField()
    created = CreationDateTimeField()

    class Meta:
        ordering = ['ordering']
        verbose_name = _("link")
        verbose_name_plural = _("links")


class Testimonial(models.Model):
    """ Any user can write something nice about a project. """

    project = models.ForeignKey(Project)
    user = models.ForeignKey('auth.User')
    description = models.TextField()
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()

    class Meta:
        ordering = ['-created']
        verbose_name = _("testimonial")
        verbose_name_plural = _("testimonials")


class Message(models.Model):
    """ Message by a user on the Project wall. """

    project = models.ForeignKey(Project)
    user = models.ForeignKey('auth.User')
    body = models.TextField()
    created = CreationDateTimeField()
    deleted = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u'%s : %s...' % (
            self.created.date(), self.body[:20]
        )

    class Meta:
        ordering = ['-created']
        verbose_name = _("message")
        verbose_name_plural = _("messages")
