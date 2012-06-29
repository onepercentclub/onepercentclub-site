'''
Created on May 24, 2012

@author: gannetson
'''
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext as _
from decimal import Decimal


class Project(models.Model):
    """ Projects. Important stuff """

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(_('slug'), max_length=255)
    title = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey('legacysystem.Country')

    organization = models.ForeignKey('legacyorganizations.Organization',
        db_column='owner_org_id'
    )
    """
    Owner_org is a Member row that refers to the organization 'user'
    That user has a reference to the Organization model
    """

    owner_usr = models.ForeignKey('legacymembers.Member')
    """ Project owner Member (Owner subclasses Member) """

    rate_current = models.FloatField()
    rate_count = models.IntegerField()

    status = models.CharField(max_length=255)

    deleted = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField()
    realised = models.DateTimeField(null=True, blank=True)
    closed = models.DateTimeField(null=True, blank=True)
    validated = models.DateTimeField(null=True, blank=True)
    """
    These dates relate to the website.
    When was the project put online, fully funded etc.
    """


    startdate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    """
    These dates are the planned dates for the implementation of this project
    """

    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)

    description = models.TextField(blank=True)
    longdescription = models.TextField(blank=True)
    money_needed_for = models.TextField(blank=True)
    project_goals = models.TextField(blank=True)
    target_audience = models.TextField(blank=True)
    solve_poverty = models.TextField(blank=True)
    planning = models.TextField(blank=True)
    expected_results = models.TextField(blank=True)
    received_other_sources = models.TextField(blank=True)
    expected_other_sources = models.TextField(blank=True)
    volunteers = models.TextField(blank=True)
    how_support = models.TextField(blank=True)
    description_duurzaamheid = models.TextField(blank=True)
    """ All kind of fields with texts describing the project """


    money_needed_club = models.CharField(max_length=255, blank=True)
    """ Money asked """

    photo = models.CharField(max_length=255, blank=True)
    legacy_budget = models.TextField(blank=True)

    project_language = models.CharField(max_length=6)
    sess_id = models.CharField(max_length=40, blank=True)
    admin_comments = models.TextField(blank=True)

    derde_helft = models.IntegerField(null=True, blank=True)
    earth_charter = models.IntegerField(null=True, blank=True)
    """ Two 'special' types, kinda whitelabeling """

    catalog = models.ForeignKey('legacyalbums.Catalog',
        unique=True, null=True, blank=True
    )
    """ Picture catalogs """
    weblog = models.ForeignKey('legacyweblog.Weblog',
        unique=True, null=True, blank=True
    )

    tags = models.ManyToManyField('legacysystem.Tag', through='ProjectTag')

    class Meta:
        db_table = u'prj_projects'
        managed = False

    def documents(self):
        return self.document_set.filter(task = None).all()

    def donated(self):
        """ Money donated """

        qs = self.donationline_set.all()
        qs = qs.filter(donation__status__in=['started','paid','closed'])

        return qs.aggregate(Sum('amount'))['amount__sum']

    def needed(self):
        """ Money still needed """

        needed = self.asked() - self.donated()

        if needed < 0:
            return 0

        return needed

    def asked(self):
        """ Money asked """
        return Decimal(self.money_needed_club)

    def donations(self):
        qs = self.donationline_set.select_related(depth=1).all()

        qs = qs.order_by('-donation__created')
        qs = qs.filter(donation__status__in=['started','paid','closed'])

        # Note: this is probably the same as [:5], what is this meant to do?
        return qs[0:5]

    def tasks(self):
        return self.task_set.all()

    def messages(self):
        return self.message_set.all()[0:5]


class MillenniumGoal(models.Model):
    """ DISCONTINUED """

    id = models.BigIntegerField(primary_key=True)
    logo = models.CharField(max_length=40, blank=True)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    shortdescription = models.TextField(blank=True)
    ordering = models.IntegerField()

    class Meta:
        db_table = u'prj_millennium_goals'
        managed = False


class Goal(models.Model):
    """ DISCONTINUED """
    """ MilimiumGoal. Connects a Project and a MilleniumGoal """

    project = models.ForeignKey(Project)
    millennium_goal = models.ForeignKey(MillenniumGoal)

    class Meta:
        db_table = u'prj_project_millennium_goals'
        managed = False


class Link(models.Model):
    """ Links connected to a Project """

    id = models.IntegerField(primary_key=True)
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    ordering = models.IntegerField()
    created = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'prj_project_links'
        managed = False


class NeedCategory(models.Model):
    """ NeedCategory?? """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True)
    description = models.TextField(blank=True)
    ordering = models.IntegerField()
    name_en = models.CharField(max_length=255, blank=True)
    name_es = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'prj_need_category'
        managed = False

    def __unicode__(self):
        return self.name


class Need(models.Model):
    id = models.IntegerField(primary_key=True)
    project = models.ForeignKey(Project)
    money_needed = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    category = models.ForeignKey(NeedCategory)

    class Meta:
        db_table = u'prj_project_needs'
        managed = False


class Reported(models.Model):
    """ EMPTY. I guess not used """
    """ Project that has been reported by a Member as being 'not ok'. """

    id = models.IntegerField(primary_key=True)
    member = models.ForeignKey('legacymembers.Member')
    project = models.ForeignKey(Project)
    content = models.TextField()
    created = models.DateTimeField()
    ip = models.CharField(max_length=50)

    class Meta:
        db_table = u'prj_project_reported'
        managed = False


class Testimonial(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.TextField()
    project = models.ForeignKey(Project)
    member = models.ForeignKey('legacymembers.Member')
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        db_table = u'prj_testimonials'
        managed = False


class ProjectTag(models.Model):
    project = models.ForeignKey(Project)
    tag = models.ForeignKey('legacysystem.Tag')

    class Meta:
        db_table = u'prj_project_tags'
        managed = False


class Video(models.Model):
    id = models.IntegerField(primary_key=True)
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    created = models.DateTimeField()
    thumb = models.CharField(max_length=255)
    watch_url = models.CharField(max_length=255)

    class Meta:
        db_table = u'prj_project_videos'
        managed = False


class Rating(models.Model):
    """ DISCONTINUED. We rather 'have thumbs up' """
    """ Seperate rating of Project by Member """

    project = models.ForeignKey(Project)
    user = models.ForeignKey('legacymembers.Member')
    rate = models.IntegerField()
    created = models.DateTimeField()

    class Meta:
        db_table = u'prj_project_rating'
        managed = False


class Message(models.Model):
    """ Message by a user on the Project wall """

    id = models.IntegerField(primary_key=True)
    project = models.ForeignKey(Project)
    member = models.ForeignKey('legacymembers.Member',
        related_name='project_message_set'
    )
    text = models.TextField()
    created = models.DateTimeField()
    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'prj_messages'
        managed = False
