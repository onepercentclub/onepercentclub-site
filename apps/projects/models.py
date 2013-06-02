from apps.wallposts.models import WallPost
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.aggregates import Count
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


class ProjectPitch(models.Model):

    class PitchStatuses(DjangoChoices):
        new = ChoiceItem('new', label=_("New"))
        submitted = ChoiceItem('submitted', label=_("Submitted"))
        rejected = ChoiceItem('rejected', label=_("Rejected"))
        needs_work = ChoiceItem('needs_work', label=_("Needs work"))
        approved = ChoiceItem('approved', label=_("Approved"))

    class NeedsChoices(DjangoChoices):
        skills = ChoiceItem('skills', label=_("Skills and expertise"))
        finance = ChoiceItem('finance', label=_("Crowdfunding campaign"))
        both = ChoiceItem('both', label=_("Both"))

    # Basics

    title = models.CharField(_("title"), max_length=100, help_text=_("Be short, creative, simple and memorable"))

    pitch = models.TextField(_("pitch"), blank=True, help_text=_("Pitch your smart idea in one sentence"))
    description = models.TextField(_("why, what and how"), help_text=_("Blow us away with the details!"), blank=True)


    created = CreationDateTimeField(_("created"), help_text=_("When this project was created."))
    updated = ModificationDateTimeField(_('updated'))

    status = models.CharField(_("status"), max_length=20, choices=PitchStatuses.choices)
    theme = models.ForeignKey(ProjectTheme, blank=True, verbose_name=_("theme"), help_text=_("Select one of the themes "))

    need = models.CharField(_("Project need"), max_length=20, choices=NeedsChoices.choices, default=NeedsChoices.both)

    tags = TaggableManager(blank=True, verbose_name=_("tags"), help_text=_("Add tags"))

    # Location

    # Location
    latitude = models.DecimalField(_("latitude"), max_digits=21, decimal_places=18)
    longitude = models.DecimalField(_("longitude"), max_digits=21, decimal_places=18)
    # country = CountryField(blank=True, null=True, verbose_name=_("country"))
    country = models.ForeignKey('geo.Country', blank=True, null=True)

    # Media
    image = ImageField(_("picture"), max_length=255, blank=True, upload_to='project_images/', help_text=_("Upload the picture that best describes your smart idea!"))
    video_url = models.URLField(_("video"), max_length=100, blank=True, default='', help_text=_("Do you have a video pitch or a short movie that explains your project. Cool! We can't wait to see it. You can paste the link to the YouTube or Vimeo video here"))

    def __unicode__(self):
        return self.title


class ProjectPlan(models.Model):

    class PitchStatuses(DjangoChoices):
        new = ChoiceItem('new', label=_("New"))
        submitted = ChoiceItem('submitted', label=_("Submitted"))
        rejected = ChoiceItem('rejected', label=_("Rejected"))
        needs_work = ChoiceItem('needs_work', label=_("Needs work"))
        approved = ChoiceItem('approved', label=_("Approved"))

    class ImpactGroups(DjangoChoices):
        children = ChoiceItem('children', label=_("Children"))
        youth = ChoiceItem('youth', label=_("Youth"))
        adults = ChoiceItem('adults', label=_("Adults"))
        elderly = ChoiceItem('elderly', label=_("Elderly"))

    # Basics

    title = models.CharField(_("title"), max_length=100, help_text=_("Be short, creative, simple and memorable"))
    slug = models.SlugField(_("slug"), max_length=100, unique=True)

    pitch = models.TextField(_("pitch"), blank=True, help_text=_("Pitch your smart idea in one sentence"))
    social_impact = models.TextField(_("social impact"), blank=True,help_text=_("Who are you helping?"))

    image = ImageField(_("image"), max_length=255, blank=True, upload_to='project_images/', help_text=_("Main project picture"))

    created = CreationDateTimeField(_("created"), help_text=_("When this project was created."))
    updated = ModificationDateTimeField(_('updated'))

    status = models.CharField(_("status"), max_length=20, choices=PitchStatuses.choices)
    theme = models.ForeignKey(ProjectTheme, blank=True, verbose_name=_("theme"), help_text=_("Select one of the themes "))

    needs_funding = models.BooleanField(_("needs funding"))
    needs_skills = models.BooleanField(_("needs skills & expertise"))

    tags = TaggableManager(blank=True, verbose_name=_("tags"), help_text=_("Add tags"))

    # Extended Description

    description = models.TextField(_("why, what and how"), help_text=_("Blow us away with the details!"), blank=True)
    effects = models.TextField(_("effects"), help_text=_("What will be the Impact? How will your Smart Idea change the lives of people?"), blank=True)
    for_who = models.TextField(_("for who"), help_text=_("Describe your target group"), blank=True)
    future = models.TextField(_("future"), help_text=_("How will this project be self-sufficient and sustainable in the long term?"), blank=True)
    reach = models.PositiveIntegerField(_("Reach"), help_text=_("How many people do you expect to reach?"), blank=True)

    # Location
    latitude = models.DecimalField(_("latitude"), max_digits=21, decimal_places=18)
    longitude = models.DecimalField(_("longitude"), max_digits=21, decimal_places=18)
    country = models.ForeignKey('geo.Country', blank=True, null=True)

    # Media
    image = ImageField(_("picture"), max_length=255, blank=True, upload_to='project_images/', help_text=_("Upload the picture that best describes your smart idea!"))
    video_url = models.URLField(_("video"), max_length=100, blank=True, default='', help_text=_("Do you have a video pitch or a short movie that explains your project. Cool! We can't wait to see it. You can paste the link to the YouTube or Vimeo video here"))

    def __unicode__(self):
        return self.title



class ProjectPhases(DjangoChoices):
    pitch = ChoiceItem('pitch', label=_("Pitch"))
    plan = ChoiceItem('plan', label=_("Plan"))
    campaign = ChoiceItem('campaign', label=_("Campaign"))
    results = ChoiceItem('results', label=_("Results"))


class Project(models.Model):
    """ The base Project model. """

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("owner"))
    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)

    pitch = models.ForeignKey('projects.ProjectPitch', null=True, blank=True)

    phase = models.CharField(_("phase"), max_length=20, choices=ProjectPhases.choices, help_text=_("Phase this project is in right now."))

    created = CreationDateTimeField(_("created"), help_text=_("When this project was created."))

    @property
    def money_donated(self):
        return 100000

    @property
    def money_asked(self):
        return 400000

    def __unicode__(self):
        if self.title:
            return self.title
        return self.slug

    @property
    def supporters_count(self, with_guests=True):
        # TODO: Replace this with a proper Supporters API
        # something like /projects/<slug>/donations
        donations = Donation.objects.filter(project=self)
        donations = donations.filter(status__in=[Donation.DonationStatuses.paid, Donation.DonationStatuses.in_progress])
        donations = donations.filter(user__isnull=False)
        donations = donations.annotate(Count('user'))
        count = len(donations.all())

        if with_guests:
            donations = Donation.objects.filter(project=self)
            donations = donations.filter(status__in=[Donation.DonationStatuses.paid, Donation.DonationStatuses.in_progress])
            donations = donations.filter(user__isnull=True)
            count = count + len(donations.all())
        return count

    @models.permalink
    def get_absolute_url(self):
        """ Get the URL for the current project. """
        return 'project-detail', (), {'slug': self.slug}

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

    sustainability = models.TextField(_("sustainability"), blank=True,help_text=_("How can next generations profit from this?"))
    money_other_sources = models.TextField(_("money from other sources"), blank=True, help_text=_("Money received from other sources."))

    # Social Impact: who are we helping, direct and indirect
    social_impact = models.TextField(_("social impact"), blank=True,help_text=_("Who are you helping?"))
    impact_group = models.CharField(_("impact group"), max_length=20, choices=ImpactGroups.choices, blank=True)
    impact_direct_male = models.IntegerField(_("impact direct male"), max_length=6, default=0)
    impact_direct_female = models.IntegerField(_("impact direct female"), max_length=6, default=0)
    impact_indirect_male = models.IntegerField(_("impact indirect male"),max_length=6, default=0)
    impact_indirect_female = models.IntegerField(_("impact indirect female"), max_length=6, default=0)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
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
