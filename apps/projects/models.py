from django.db import models
from django.utils.translation import ugettext as _

from django_countries import CountryField
from djchoices import DjangoChoices, ChoiceItem
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField, AutoSlugField


class Project(models.Model):
    """ The base Project model """

    class ProjectPhases(DjangoChoices):
        idea = ChoiceItem('idea', label=_('idea'))
        plan = ChoiceItem('plan', label=_('plan'))
        act = ChoiceItem('act', label=_('act'))
        results = ChoiceItem('results', label=_('results'))

    slug = models.SlugField(max_length=100)
    title = models.CharField(max_length=255)

    photo = models.CharField(max_length=255, blank=True)
    """ Main project picture """

    organization = models.ForeignKey('organizations.Organization')
    owner = models.ForeignKey('auth.User')

    phase = models.CharField(max_length=20, choices=ProjectPhases.choices)
    """ Phase this project is in right now """

    created = CreationDateTimeField()
    """ When was this project created """

    country = CountryField(null=True)
    latitude = models.CharField(max_length=30)
    longitude = models.CharField(max_length=30)
    """ Location of this project """

    project_language = models.CharField(max_length=6)
    """ Main language (now 'en' or 'nl') """

    def __unicode__(self):
        if self.title:
            return self.title
        return self.slug

    class Meta:
        ordering = ['title']


class AbstractPhase(models.Model):
    class PhaseStatuses(DjangoChoices):
        hidden = ChoiceItem('hidden', label=_('hidden'))
        progress = ChoiceItem('progress', label=_('progress'))
        completed = ChoiceItem('completed', label=_('completed'))

    project = models.OneToOneField(Project)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    startdate = models.DateField(null=True)
    enddate = models.DateField(null=True)
    """ Date the phase has started/ended """

    status = models.CharField(max_length=20, choices=PhaseStatuses.choices)

    class Meta:
        abstract = True


class IdeaPhase(AbstractPhase):
    """ IdeaPhase: Got a nice idea here """


class PlanPhase(AbstractPhase):
    """ PlanPhase: fill out some forms for project plan """

    class PhaseStatuses(DjangoChoices):
        hidden = ChoiceItem('hidden', label=_('hidden'))
        progress = ChoiceItem('progress', label=_('progress'))
        feedback = ChoiceItem('feedback', label=_('feedback'))
        waiting = ChoiceItem('waiting', label=_('waiting'))
        completed = ChoiceItem('completed', label=_('completed'))

    money_total = models.DecimalField(max_digits=9, decimal_places=2)
    """ Amount needed for this project (total) """
    money_asked = models.DecimalField(max_digits=9, decimal_places=2)
    """ Amount asked from this website """

    what = models.TextField(_("What do you want to do?"), blank=True)
    goal = models.TextField(_("What is your goal?"), blank=True)
    who = models.TextField(_("Who are you helping?"), blank=True)
    how = models.TextField(_("In which way?"), blank=True)
    sustainability = models.TextField(_("How can next generations profit from this?"), blank=True)
    target = models.TextField(_("What is your target?"), blank=True)
    needed_expertise = models.TextField(blank=True)
    needed_volunteers = models.TextField(blank=True)

    budget_description = models.TextField(blank=True)
    money_other_sources = models.TextField(blank=True)



class ActPhase(AbstractPhase):
    """ ActPhase Funding complete lets DO it! """

    planning = models.TextField(blank=True)
    planned_start_date = models.DateField(null=True)
    planned_end_date = models.DateField(null=True)


class ResultsPhase(AbstractPhase):
    """ ResultsPhase: Tell about how things worked out """

    what = models.TextField(_("What and how?"), blank=True)
    tips = models.TextField(_("Tips and tricks?"), blank=True)
    change = models.TextField(_("What has changed for the target group?"), blank=True)
    financial = models.TextField(_("How was the money spend?"), blank=True)
    next = models.TextField(_("What's next?"), blank=True)
    """ Five questions that get asked after the project is done """


class BudgetCategory(models.Model):
    """ BudgetCategory: Categories for BudgetLines """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    ordering = models.IntegerField(max_length=3)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['ordering']
        verbose_name_plural = 'Budget Categories'

class BudgetLine(models.Model):
    """ 
        BudgetLine: Entries to the Project Budget sheet.
        This is the budget for the amount asked from this
        website. 
    """

    project = models.ForeignKey(Project)
    category = models.ForeignKey(BudgetCategory)
    description = models.TextField(blank=True)
    money_amount = models.DecimalField(max_digits=9, decimal_places=2)


class OtherSourcesLines(models.Model):
    """ 
        Other sources of money to fund this project.
        Every entry is an application (-to apply-) 
        for a grant or other probable source of money.
    """

    class Statuses(DjangoChoices):
        progress = ChoiceItem('progress', label=_('progress'))
        applied = ChoiceItem('applied', label=_('applied'))
        granted = ChoiceItem('granted', label=_('granted'))
        received = ChoiceItem('received', label=_('received'))

    project = models.ForeignKey(Project)
    source = models.CharField(max_length=255)
    """ Who's giving the money """
    description = models.TextField(blank=True)
    money_amount = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=20, choices=Statuses.choices)


# Now some stuff connected to Projects
# Can we think of a better place to put this??    

class Link(models.Model):
    """ Links (urls) connected to a Project """
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(blank=True)
    ordering = models.IntegerField()
    created = CreationDateTimeField()

    class Meta:
        ordering = ['ordering']


class Testimonial(models.Model):
    """ Any member can write something nice about a project """
    project = models.ForeignKey(Project)
    member = models.ForeignKey('auth.User')
    description = models.TextField()
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()

    class Meta:
        ordering = ['-created']


class Message(models.Model):
    """ Message by a user on the Project wall """
    project = models.ForeignKey(Project)
    member = models.ForeignKey('auth.User')
    description = models.TextField()
    created = CreationDateTimeField()
    deleted = models.DateTimeField(null=True)

    def __unicode__(self):
        return str(self.created.date()) + ' : ' + self.description[:80] + '...'

    class Meta:
        ordering = ['-created']

