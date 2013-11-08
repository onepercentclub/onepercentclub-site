import datetime
from apps.tasks.models import Task
from babel.numbers import format_currency
from django.db import models
from django.db.models.aggregates import Count, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import translation
from django.utils.translation import ugettext as _
from django.conf import settings
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from sorl.thumbnail import ImageField
from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager
from apps.fund.models import Donation, DonationStatuses
from django.template.defaultfilters import slugify
from django.utils import timezone
from .mails import mail_project_funded_internal
from .signals import project_funded


class ProjectTheme(models.Model):
    """ Themes for Projects. """

    # The name is marked as unique so that users can't create duplicate theme names.
    name = models.CharField(_("name"), max_length=100, unique=True)
    name_nl = models.CharField(_("name"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)
    description = models.TextField(_("description"), blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("project theme")
        verbose_name_plural = _("project themes")


class ProjectPhases(DjangoChoices):
    pitch = ChoiceItem('pitch', label=_("Pitch"))
    plan = ChoiceItem('plan', label=_("Plan"))
    campaign = ChoiceItem('campaign', label=_("Campaign"))
    act = ChoiceItem('act', label=_("Act"))
    results = ChoiceItem('results', label=_("Results"))
    realized = ChoiceItem('realized', label=_("Realised"))
    failed = ChoiceItem('failed', label=_("Failed"))


class ProjectPhaseLog(models.Model):
    """ Log when a project reaches a certain phase """
    
    project = models.ForeignKey('projects.Project')
    phase = models.CharField(_("phase"), max_length=20, choices=ProjectPhases.choices)
    created = CreationDateTimeField(_("created"), help_text=_("When this phase was reached."))

    class Meta:
        unique_together = (('project', 'phase'),)

    def __unicode__(self):
        return "%s - %s - %s" % (
                self.project.title,
                self.phase,
                self.created
            )


class ProjectManager(models.Manager):

    def order_by(self, field):

        if field == 'money_asked':
            qs = self.get_query_set()
            qs = qs.filter(phase__in=[ProjectPhases.campaign, ProjectPhases.act, ProjectPhases.results, ProjectPhases.realized])
            qs = qs.order_by('projectcampaign__money_asked')
            return qs

        if field == 'deadline':
            qs = self.get_query_set()
            qs = qs.filter(phase=ProjectPhases.campaign)
            qs = qs.order_by('projectcampaign__deadline')
            qs = qs.filter(phase='campaign')
            return qs

        if field == 'money_needed':
            qs = self.get_query_set()
            qs = qs.order_by('projectcampaign__money_asked')
            qs = qs.filter(phase='campaign')
            return qs

        if field == 'donations':
            qs = self.get_query_set()
            qs = qs.order_by('popularity')
            return qs

        qs = super(ProjectManager, self).order_by(field)
        return qs


class Project(models.Model):
    """ The base Project model. """

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("initiator"), help_text=_("Project owner"), related_name="owner")

    coach = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("coach"), help_text=_("Assistent at 1%OFFICE"), related_name="team_member", null=True, blank=True)

    title = models.CharField(_("title"), max_length=255, unique=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)

    phase = models.CharField(_("phase"), max_length=20, choices=ProjectPhases.choices, help_text=_("Phase this project is in right now."))

    partner_organization = models.ForeignKey('projects.PartnerOrganization', null=True, blank=True)

    created = CreationDateTimeField(_("created"), help_text=_("When this project was created."))
    updated = ModificationDateTimeField()

    popularity = models.FloatField(null=False, default=0)

    objects = ProjectManager()

    _original_phase = None

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        # we do this for efficiency reasons. Comparing with the object in database
        # through a pre_save handler is expensive because it requires at least one
        # extra query. The phase logging is handled in a post_save only when it's
        # needed!
        self._original_phase = self.phase

    def __unicode__(self):
        if self.title:
            return self.title
        return self.slug

    def update_popularity(self):
        last_month = timezone.now() - timezone.timedelta(days=30)
        donations = Donation.objects.filter(status__in=[DonationStatuses.paid, DonationStatuses.pending])
        donations = donations.exclude(donation_type='recurring')
        donations = donations.filter(created__gte=last_month)

        # For all projects.
        total_recent_donors = len(donations)
        total_recent_donations = donations.aggregate(sum=Sum('amount'))['sum']
        # For this project
        donations = donations.filter(project=self)
        recent_donors = len(donations)
        recent_donations = donations.aggregate(sum=Sum('amount'))['sum']

        if recent_donors and recent_donations:
            self.popularity = 50 * (float(recent_donors) / float(total_recent_donors)) + 50 * (float(recent_donations) / float(total_recent_donations))
        else:
            self.popularity = 0
        self.save()

    @property
    def supporters_count(self, with_guests=True):
        # TODO: Replace this with a proper Supporters API
        # something like /projects/<slug>/donations
        donations = Donation.objects.filter(project=self)
        donations = donations.filter(status__in=[DonationStatuses.paid, DonationStatuses.in_progress])
        donations = donations.filter(user__isnull=False)
        donations = donations.annotate(Count('user'))
        count = len(donations.all())

        if with_guests:
            donations = Donation.objects.filter(project=self)
            donations = donations.filter(status__in=[DonationStatuses.paid, DonationStatuses.in_progress])
            donations = donations.filter(user__isnull=True)
            count = count + len(donations.all())
        return count

    @property
    def task_count(self):
        return len(self.task_set.filter(status=Task.TaskStatuses.open).all())

    @property
    def get_open_tasks(self):
        return self.task_set.filter(status=Task.TaskStatuses.open).all()

    @property
    def date_funded(self):
        try:
            log = self.projectphaselog_set.get(phase=ProjectPhases.act)
            return log.created
        except ProjectPhaseLog.DoesNotExist:
            # fall back to creation date of the projectresult
            if self.projectresult:
                return self.projectresult.created
        return None

    @models.permalink
    def get_absolute_url(self):
        """ Get the URL for the current project. """
        return 'project-detail', (), {'slug': self.slug}

    def get_absolute_frontend_url(self):
        url = self.get_absolute_url()
        # insert the hashbang, after the language string
        bits = url.split('/')
        url = "/".join(bits[:2] + ['#!'] + bits[2:])
        return url

    def get_meta_title(self, **kwargs):
        plan = self.projectplan
        return u"%(name_project)s | %(theme)s | %(country)s" % {
            'name_project': self.title,
            'theme': plan.theme.name if plan.theme else '',
            'country': plan.country.name if plan.country else '',
        }

    def get_fb_title(self, **kwargs):
        plan = self.projectplan
        title = _(u"{name_project} in {country}").format(
                    name_project = self.title,
                    country = plan.country.name if plan.country else '',
                )
        return title

    def get_tweet(self, **kwargs):
        """ Build the tweet text for the meta data """
        request = kwargs.get('request')
        lang_code = request.LANGUAGE_CODE
        twitter_handle = settings.TWITTER_HANDLES.get(lang_code, settings.DEFAULT_TWITTER_HANDLE)

        title = self.get_fb_title()

        # {URL} is replaced in Ember to fill in the page url, avoiding the
        # need to provide front-end urls in our Django code.
        tweet = _(u"{title} {{URL}} via @{twitter_handle}").format(
                    title=title, twitter_handle=twitter_handle
                )

        return tweet

    class Meta:
        ordering = ['title']
        verbose_name = _("project")
        verbose_name_plural = _("projects")

    def save(self, *args, **kwargs):
        if not self.slug:
            original_slug = slugify(self.title)
            counter = 2
            qs = Project.objects
            while qs.filter(slug = original_slug).exists():
                original_slug = '%s-%d' % (original_slug, counter)
                counter += 1
            self.slug = original_slug

        if not self.phase:
            self.phase = ProjectPhases.pitch
        super(Project, self).save(*args, **kwargs)


class ProjectNeedChoices(DjangoChoices):
    skills = ChoiceItem('skills', label=_("Skills and expertise"))
    finance = ChoiceItem('finance', label=_("Crowdfunding campaign"))
    both = ChoiceItem('both', label=_("Both"))


class ProjectPitch(models.Model):

    class PitchStatuses(DjangoChoices):
        new = ChoiceItem('new', label=_("New"))
        submitted = ChoiceItem('submitted', label=_("Submitted"))
        rejected = ChoiceItem('rejected', label=_("Rejected"))
        approved = ChoiceItem('approved', label=_("Approved"))

    project = models.OneToOneField("projects.Project", verbose_name=_("project"))
    status = models.CharField(_("status"), max_length=20, choices=PitchStatuses.choices)

    created = CreationDateTimeField(_("created"), help_text=_("When this project was created."))
    updated = ModificationDateTimeField(_('updated'))

    # Basics
    title = models.CharField(_("title"), max_length=100, help_text=_("Be short, creative, simple and memorable"))
    pitch = models.TextField(_("pitch"), blank=True, help_text=_("Pitch your smart idea in one sentence"))
    description = models.TextField(_("why, what and how"), help_text=_("Blow us away with the details!"), blank=True)

    need = models.CharField(_("Project need"), null=True, max_length=20, choices=ProjectNeedChoices.choices, default=ProjectNeedChoices.both)
    theme = models.ForeignKey(ProjectTheme, blank=True, null=True, verbose_name=_("theme"), help_text=_("Select one of the themes "))
    tags = TaggableManager(blank=True, verbose_name=_("tags"), help_text=_("Add tags"))

    # Location
    latitude = models.DecimalField(_("latitude"), max_digits=21, decimal_places=18, null=True, blank=True)
    longitude = models.DecimalField(_("longitude"), max_digits=21, decimal_places=18, null=True, blank=True)
    country = models.ForeignKey('geo.Country', blank=True, null=True)

    # Media
    image = ImageField(_("picture"), max_length=255, blank=True, null=True, upload_to='project_images/', help_text=_("Upload the picture that best describes your smart idea!"))
    video_url = models.URLField(_("video"), max_length=100, blank=True, default='', help_text=_("Do you have a video pitch or a short movie that explains your project. Cool! We can't wait to see it. You can paste the link to the YouTube or Vimeo video here"))

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('pitch')
        verbose_name_plural = _('pitches')


class ProjectPlan(models.Model):

    class PlanStatuses(DjangoChoices):
        new = ChoiceItem('new', label=_("New"))
        submitted = ChoiceItem('submitted', label=_("Submitted"))
        rejected = ChoiceItem('rejected', label=_("Rejected"))
        needs_work = ChoiceItem('needs_work', label=_("Needs work"))
        approved = ChoiceItem('approved', label=_("Approved"))

    project = models.OneToOneField("projects.Project", verbose_name=_("project"))
    status = models.CharField(_("status"), max_length=20, choices=PlanStatuses.choices)

    created = CreationDateTimeField(_("created"), help_text=_("When this project was created."))
    updated = ModificationDateTimeField(_('updated'))

    # Basics
    title = models.CharField(_("title"), max_length=100, help_text=_("Be short, creative, simple and memorable"))
    pitch = models.TextField(_("pitch"), blank=True, help_text=_("Pitch your smart idea in one sentence"))

    need = models.CharField(_("Project need"), null=True, max_length=20, choices=ProjectNeedChoices.choices, default=ProjectNeedChoices.both)
    theme = models.ForeignKey(ProjectTheme, blank=True, null=True, verbose_name=_("theme"), help_text=_("Select one of the themes "))
    tags = TaggableManager(blank=True, verbose_name=_("tags"), help_text=_("Add tags"))

    # Extended Description
    description = models.TextField(_("why, what and how"), help_text=_("Blow us away with the details!"), blank=True)
    effects = models.TextField(_("effects"), help_text=_("What will be the Impact? How will your Smart Idea change the lives of people?"), blank=True)
    for_who = models.TextField(_("for who"), help_text=_("Describe your target group"), blank=True)
    future = models.TextField(_("future"), help_text=_("How will this project be self-sufficient and sustainable in the long term?"), blank=True)
    reach = models.PositiveIntegerField(_("Reach"), help_text=_("How many people do you expect to reach?"), blank=True, null=True)

    # Location
    latitude = models.DecimalField(_("latitude"), max_digits=21, decimal_places=18, null=True, blank=True)
    longitude = models.DecimalField(_("longitude"), max_digits=21, decimal_places=18, null=True, blank=True)
    country = models.ForeignKey('geo.Country', blank=True, null=True)

    # Media
    image = ImageField(_("image"), max_length=255, blank=True, upload_to='project_images/', help_text=_("Main project picture"))
    video_url = models.URLField(_("video"), max_length=100, blank=True, null=True, default='', help_text=_("Do you have a video pitch or a short movie that explains your project. Cool! We can't wait to see it. You can paste the link to the YouTube or Vimeo video here"))

    organization = models.ForeignKey('organizations.Organization', verbose_name=_("organisation"), blank=True, null=True)

    # Crowd funding
    money_needed = models.TextField(blank=True, help_text=_("Describe in one sentence what you need the money for."))
    campaign = models.TextField(_("Campaign strategy"), blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('plan')
        verbose_name_plural = _('plans')


class ProjectCampaign(models.Model):

    class CampaignStatuses(DjangoChoices):
        running = ChoiceItem('running', label=_("Running"))
        realized = ChoiceItem('realized', label=_("Realized"))
        closed = ChoiceItem('closed', label=_("Closed"))

    project = models.OneToOneField("projects.Project", verbose_name=_("project"))
    status = models.CharField(_("status"), max_length=20, choices=CampaignStatuses.choices)

    deadline = models.DateTimeField(null=True)
    payout_date = models.DateTimeField(null=True)

    created = CreationDateTimeField(_("created"), help_text=_("When this project was created."))
    updated = ModificationDateTimeField(_('updated'))

    currency = models.CharField(max_length="10", default='EUR')

    # For convenience and performance we also store money donated and needed here.
    money_asked = models.PositiveIntegerField(default=0)
    money_donated = models.PositiveIntegerField(default=0)
    money_needed = models.PositiveIntegerField(default=0)

    @property
    def nr_days_remaining(self):
        """ Return the number of days that remain before the deadline passes """
        if not self.deadline:
            return 0
        days = (self.deadline.date() - datetime.date.today()).days
        if days < 0:
            return 0
        return days

    @property
    def percentage_funded(self):
        """ Return a float containing the percentage of funds still required for this campaign """
        if not self.money_donated or not self.money_asked:
            return 0.0
        if self.status != 'running' or self.money_donated > self.money_asked:
            return 100.0
        return self.money_donated / (self.money_asked / 100.0)

    @property
    def local_money_asked(self, currency='EUR'):
        # TODO: Make this currency aware and move it to a more sensible place like view.
        return self.money_asked / 100

    @property
    def local_money_donated(self, currency='EUR'):
        # TODO: Make this currency aware and move it to a more sensible place like view.
        return self.money_donated / 100

    @property
    def local_money_needed(self, currency='EUR'):
        # TODO: Make this currency aware and move it to a more sensible place like view.
        return self.money_needed / 100

    @property
    def supporters_count(self, with_guests=True):
        # TODO: Replace this with a proper Supporters API
        # something like /projects/<slug>/donations
        donations = Donation.objects.filter(project=self.project)
        donations = donations.filter(status__in=[DonationStatuses.paid, DonationStatuses.pending])
        donations = donations.filter(user__isnull=False)
        donations = donations.annotate(Count('user'))
        count = len(donations.all())

        if with_guests:
            donations = Donation.objects.filter(project=self.project)
            donations = donations.filter(status__in=[DonationStatuses.paid, DonationStatuses.pending])
            donations = donations.filter(user__isnull=True)
            count += len(donations.all())
        return count

    # The amount donated that is secure.
    @property
    def money_safe(self):
        if self.money_asked == 0:
            return 0
        donations = Donation.objects.filter(project=self.project)
        donations = donations.filter(status__in=[DonationStatuses.paid])
        total = donations.aggregate(sum=Sum('amount'))
        if not total['sum']:
            return 0
        return total['sum']

    def update_money_donated(self):
        donations = Donation.objects.filter(project=self.project)
        donations = donations.filter(status__in=[DonationStatuses.paid, DonationStatuses.pending])
        total = donations.aggregate(sum=Sum('amount'))
        if not total['sum']:
            self.money_donated = 0
        else:
            self.money_donated = total['sum']
        self.money_needed = self.money_asked - self.money_donated
        if self.money_needed < 0:
            self.money_needed = 0
        self.save()


class ProjectResult(models.Model):

    class ResultStatuses(DjangoChoices):
        running = ChoiceItem('running', label=_("Running"))
        realized = ChoiceItem('realized', label=_("Realized"))
        closed = ChoiceItem('closed', label=_("Closed"))

    project = models.OneToOneField("projects.Project", verbose_name=_("project"))
    status = models.CharField(_("status"), max_length=20, choices=ResultStatuses.choices)

    created = CreationDateTimeField(_("created"), help_text=_("When this project was created."))
    updated = ModificationDateTimeField(_('updated'))


class PartnerOrganization(models.Model):
    """
        Some projects are run in cooperation with a partner
        organization like EarthCharter & MacroMicro
    """
    name = models.CharField(_("name"), max_length=255, unique=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)
    description = models.TextField(_("description"))
    image = ImageField(_("image"), max_length=255, blank=True, null=True, upload_to='partner_images/', help_text=_("Main partner picture"))

    @property
    def projects(self):
        return self.project_set.exclude(phase__in=['pitch', 'failed']).all()

    class Meta:
        verbose_name = _("partner organization")
        verbose_name_plural = _("partner organizations")

    def __unicode__(self):
        if self.name:
            return self.name
        return self.slug


class ProjectAmbassador(models.Model):
    """
    People that are named as an ambassador.
    """
    project_plan = models.ForeignKey(ProjectPlan)
    name = models.CharField(_("name"), max_length=255)
    email = models.EmailField(_("email"))
    description = models.TextField(_("description"))


class ProjectBudgetLine(models.Model):
    """
    BudgetLine: Entries to the Project Budget sheet.
    This is the budget for the amount asked from this
    website.
    """
    project_plan = models.ForeignKey(ProjectPlan)
    description = models.CharField(_("description"), max_length=255, default='')
    currency = models.CharField(max_length=3, default='EUR')
    amount = models.PositiveIntegerField(_("amount (in cents)"))

    created = CreationDateTimeField()
    updated = ModificationDateTimeField()

    class Meta:
        verbose_name = _("budget line")
        verbose_name_plural = _("budget lines")

    def __unicode__(self):
        language = translation.get_language().split('-')[0]
        if not language:
            language = 'en'
        return u'{0} - {1}'.format(self.description,
                                   format_currency(self.amount / 100.0, self.currency, locale=language))


@receiver(post_save, weak=False, sender=Project, dispatch_uid="log-project-phase")
def log_project_phase(sender, instance, created, **kwargs):
    """ Log the project phases when they change """
    if instance.phase != instance._original_phase or created:
        phase = getattr(ProjectPhases, instance.phase)
        # get or create to handle IntegrityErrors (unique constraints)
        # manually reverting a project phase causes violations of the constraint
        log_instance, log_created = instance.projectphaselog_set.get_or_create(phase=phase)

        # Send the project_funded signal if the campaign phase has ended and the act phased is starting.
        # This needs to be in this method instead of in its own method because 'instance._original_phase' is modified
        # below which makes it impossible to use 'instance._original_phase' condition in another post_save method.
        if instance._original_phase == ProjectPhases.campaign and phase == ProjectPhases.act:
            project_funded.send(sender=Project, instance=instance, first_time_funded=log_created)

        # set the new phase as 'original', as subsequent saves can occur,
        # leading to unique_constraints being violated (plan_status_status_changed)
        # for example
        instance._original_phase = instance.phase


@receiver(project_funded, weak=False, sender=Project, dispatch_uid="email-project-team-project-funded")
def email_project_team_project_funded(sender, instance, first_time_funded, **kwargs):
    mail_project_funded_internal(instance)


@receiver(post_save, weak=False, sender=Project)
def progress_project_phase(sender, instance, created, **kwargs):
    # Skip all post save logic during fixture loading.
    if kwargs.get('raw', False):
        return

    # If a new project is created it should have a pitch
    try:
        instance.projectpitch
    except ProjectPitch.DoesNotExist:
        instance.projectpitch = ProjectPitch(project=instance)
        instance.projectpitch.title = instance.title
        instance.projectpitch.status = ProjectPitch.PitchStatuses.new
        instance.projectpitch.save()

    if instance.phase == ProjectPhases.pitch:
        # If project is rolled back to Pitch (e.g. from Plan) then adjust Pitch status.
        if instance.projectpitch.status == ProjectPitch.PitchStatuses.approved:
            instance.projectpitch.status = ProjectPitch.PitchStatuses.new
            instance.projectpitch.save()

    # If phase progresses to 'plan' we should create and populate a ProjectPlan.
    if instance.phase == ProjectPhases.plan:
        try:
            instance.projectplan
        except ProjectPlan.DoesNotExist:
            # Create a ProjectPlan if it's not there yet
            instance.projectplan = ProjectPlan.objects.create(project=instance)
            instance.projectplan.status = ProjectPlan.PlanStatuses.new
            # Get the Pitch and copy over all fields to the new Plan
            try:
                for field in ['country', 'title', 'description', 'image', 'latitude', 'longitude', 'need', 'pitch',
                              'image', 'video_url', 'theme']:
                    setattr(instance.projectplan, field, getattr(instance.projectpitch, field))
                instance.projectplan.save()
                # After the plan is saved we can add tags
                for tag in instance.projectpitch.tags.all():
                    instance.projectplan.tags.add(tag.name)

                if instance.projectpitch.status != ProjectPitch.PitchStatuses.approved:
                    instance.projectpitch.status = ProjectPitch.PitchStatuses.approved
                    instance.projectpitch.save()

            except ProjectPitch.DoesNotExist:
                # This would normally only happen during migrations, so please ignore.
                pass

    # If phase progresses to 'campaign' we should change status on ProjectPlan.
    if instance.phase == ProjectPhases.campaign:
        try:
            # Set the correct statuses and save pitch and plan
            if instance.projectplan.status != ProjectPlan.PlanStatuses.approved:
                instance.projectplan.status = ProjectPlan.PlanStatuses.approved
                instance.projectplan.save()

            if instance.projectpitch.status != ProjectPitch.PitchStatuses.approved:
                instance.projectpitch.status = ProjectPitch.PitchStatuses.approved
                instance.projectpitch.save()
        except ProjectPlan.DoesNotExist:
            # This would normally only happen during migrations, so please ignore.
            pass

        # If we don't have a Campaign then create one and set the deadline and money_asked (based on ProjectBudgetLines).
        try:
            instance.projectcampaign
        except ProjectCampaign.DoesNotExist:
            # Set Campaign to running and set the Deadline and MoneyAsked (based on ProjectBudgetLines).
            instance.projectcampaign = ProjectCampaign.objects.create(project=instance)
            instance.projectcampaign.status = ProjectCampaign.CampaignStatuses.running
            instance.projectcampaign.deadline = timezone.now() + timezone.timedelta(days=180)

            budget = instance.projectplan.projectbudgetline_set
            if len(budget.all()):
                budget = budget.aggregate(sum=Sum('amount'))['sum']
            else:
                budget = 0
            instance.projectcampaign.money_asked = budget
            instance.projectcampaign.currency = 'EUR'
            instance.projectcampaign.save()


@receiver(post_save, weak=False, sender=ProjectPitch)
def pitch_status_status_changed(sender, instance, created, **kwargs):
    # Skip all post save logic during fixture loading.
    if kwargs.get('raw', False):
        return

    project_saved = False

    # If Pitch is approved, move Project to Plan phase.
    if instance.status == ProjectPitch.PitchStatuses.approved:
        if instance.project.phase == ProjectPhases.pitch:
            instance.project.phase = ProjectPhases.plan
            instance.project.save()
            project_saved = True

    # Ensure the project 'updated' field is updated for the Salesforce sync script.
    if not project_saved:
        instance.project.save()


@receiver(post_save, weak=False, sender=ProjectPlan)
def plan_status_status_changed(sender, instance, created, **kwargs):

    project_saved = False

    # If plan is approved the move Project to Campaign phase.
    if instance.status == ProjectPlan.PlanStatuses.approved:
        if instance.project.phase == ProjectPhases.plan:
            instance.project.phase = ProjectPhases.campaign
            instance.project.save()
            project_saved = True

    # Ensure the project 'updated' field is updated for the Salesforce sync script.
    if not project_saved:
        instance.project.save()


@receiver(post_save, weak=False, sender=ProjectCampaign, dispatch_uid="update-project-after-campaign-updated")
def update_project_after_campaign_updated(sender, instance, created, **kwargs):
    """ Ensure the project 'updated' field is updated for the Salesforce sync script. """
    instance.project.save()


# Change project phase according to donated amount
@receiver(post_save, weak=False, sender=Donation)
def update_project_after_donation(sender, instance, created, **kwargs):
    # Skip all post save logic during fixture loading.
    if kwargs.get('raw', False):
        return

    project = instance.project
    campaign = project.projectcampaign

    # Don't look at donations that are just created.
    if instance.status not in [DonationStatuses.in_progress, DonationStatuses.new]:
        campaign.update_money_donated()
        project.update_popularity()

    if campaign.money_asked <= campaign.money_donated:
        project.phase = ProjectPhases.act
        project.save()
    else:
        project.phase = ProjectPhases.campaign
        project.save()
