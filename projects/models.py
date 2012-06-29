from django.db import models
from django_countries import CountryField


class Project(models.Model):
    """ The base Project model """
    PHASES = (
        ('i', 'idea'),
        ('p', 'plan'),
        ('a', 'act'),
        ('r', 'results'),
    )
    slug = models.CharField(max_length=100)
    title = models.CharField(max_length=255)

    photo = models.CharField(max_length=255, null=True)
    """
        Main project picture
    """

    organization = models.ForeignKey('organizations.Organization')
    owner = models.ForeignKey('auth.User')

    phase = models.CharField(max_length=1, choices=PHASES)
    """ Phase this project is in right now """

    created = models.DateTimeField()
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
        ordering =  ['title']


class AbstractPhase(models.Model):
    STATUSES = (
        ('h', 'hidden'),
        ('p', 'in progress'),
        ('c', 'completed'),
    )
    project = models.OneToOneField(Project)
    title = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)

    startdate = models.DateField(null=True)
    enddate = models.DateField(null=True)
    """ Date the phase has started/ended """

    status = models.CharField(max_length=1, choices=STATUSES)

    class Meta:
        abstract = True


class IdeaPhase(AbstractPhase):
    """ IdeaPhase: Got a nice idea here """

class PlanPhase(AbstractPhase):
    """ PlanPhase: fill out some forms for project plan """

    STATUSES = (
        ('h', 'hidden'),
        ('p', 'in progress'),
        ('f', 'feedback'),
        ('w', 'waiting'),
        ('c', 'completed'),
    )

    money_total = models.FloatField()
    """ Amount needed for this project (total) """
    money_asked = models.FloatField()
    """ Amount asked from this website """

    what = models.TextField(null=True)
    goal = models.TextField(null=True)
    who = models.TextField(null=True)
    how = models.TextField(null=True)
    sustainability = models.TextField(null=True)
    target = models.TextField(null=True)
    needed_expertise = models.TextField(null=True)
    needed_volunteers = models.TextField(null=True)

    budget_description = models.TextField(null=True)
    money_other_sources = models.TextField(null=True)



class ActPhase(AbstractPhase):
    """ ActPhase Funding complete lets DO it! """

    planning = models.TextField(null=True)
    planned_start_date = models.DateField(null=True)
    planned_end_date = models.DateField(null=True)
    

class ResultsPhase(AbstractPhase):
    """ ResultsPhase: Tell about how things worked out """

    what = models.TextField(null=True)
    tips = models.TextField(null=True)
    change = models.TextField(null=True)
    financial = models.TextField(null=True)
    next = models.TextField(null=True)
    """ Five questions that get asked after the project is done """


class BudgetCategory(models.Model):
    """ BudgetCategory: Categories for BudgetLines """

    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True)
    description = models.TextField(null=True)
    ordering = models.IntegerField(max_length=3)

    def __unicode__(self):
        if self.parent:
            return self.parent.name + ' - ' + self.name
        return self.name
    
    class Meta:
        ordering =  ['ordering']
        verbose_name_plural = 'Budget Categories'

class BudgetLine(models.Model):
    """ 
        BudgetLine: Entries to the Project Budget sheet.
        This is the budget for the amount asked from this
        website. 
    """

    project = models.ForeignKey(Project)
    category = models.ForeignKey(BudgetCategory)
    description = models.TextField(null=True)
    money_amount = models.FloatField()


class OtherSourcesLines(models.Model):
    """ 
        Other sources of money to fund this project.
        Every entry is an application (-to apply-) 
        for a grant or other probable source of money.
    """

    STATUSES = (
        ('p', 'in progress'),
        ('a', 'applied'),
        ('g', 'granted'),
        ('r', 'received'),
    )

    project = models.ForeignKey(Project)
    source = models.CharField(max_length=255)
    """ Who's giving the money """
    description = models.TextField(null=True)
    money_amount = models.FloatField()
    status = models.CharField(max_length=1, choices=STATUSES)


# Now some stuff connected to Projects
# Can we think of a better place to put this??    
    
class Link(models.Model):
    """ Links (urls) connected to a Project """
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    ordering = models.IntegerField()
    created = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering =  ['ordering']


class Testimonial(models.Model):
    """ Any member can write something nice about a project """
    project = models.ForeignKey(Project)
    member = models.ForeignKey('auth.User')
    description = models.TextField()
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        ordering =  ['-created']


class Message(models.Model):
    """ Message by a user on the Project wall """
    project = models.ForeignKey(Project)
    member = models.ForeignKey('auth.User')
    description = models.TextField()
    created = models.DateTimeField()
    deleted = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return str(self.created.date()) + ' : ' + self.description[:80] + '...'
    
    class Meta:
        ordering =  ['-created']
    
    