from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField


from djchoices.choices import DjangoChoices, ChoiceItem
from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager


from bluebottle.bluebottle_utils.utils import clean_for_hashtag


class Skill(models.Model):

    name = models.CharField(_("english name"), max_length=100, unique=True)
    name_nl = models.CharField(_("dutch name"), max_length=100, unique=True)
    description = models.TextField(_("description"), blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('id', )


class Task(models.Model):
    """ Tasks """

    class TaskStatuses(DjangoChoices):
        open = ChoiceItem('open', label=_("Open"))
        in_progress = ChoiceItem('in progress', label=_("In progress"))
        closed = ChoiceItem('closed', label=_("Closed"))
        realized = ChoiceItem('realized', label=_("Realised"))

    title = models.CharField(_("title"), max_length=100)
    description = models.TextField(_("description"))
    end_goal = models.TextField(_("end goal"))
    location = models.CharField(_("location"), max_length=200)

    expertise = models.CharField(_("old expertise"), max_length=200)
    skill = models.ForeignKey(Skill, verbose_name=_("Skill needed"), null=True)
    time_needed = models.CharField(_("time_needed"), max_length=200, help_text=_("Estimated number of hours needed to perform this task."))

    status = models.CharField(_("status"), max_length=20, choices=TaskStatuses.choices, default=TaskStatuses.open)

    people_needed = models.PositiveIntegerField(_("people needed"), default=1, help_text=_("How many people are needed for this task?"))

    project = models.ForeignKey('projects.Project')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='author')
    created = CreationDateTimeField(_("created"), help_text=_("When this task was created?"))
    updated = ModificationDateTimeField(_("updated"))

    tags = TaggableManager(blank=True, verbose_name=_("tags"))

    deadline = models.DateTimeField()

    def __unicode__(self):
        return self.title

    def get_meta_title(self, **kwargs):
        from apps.projects.models import ProjectPlan
        try:
            plan = self.project.projectplan
            country = plan.country.name if plan.country else ''
        except ProjectPlan.DoesNotExist:
            country = ''
        return u"%(task_name)s | %(expertise)s | %(country)s" % {
            'task_name': self.title,
            'expertise': self.skill.name if self.skill else '',
            'country': country,
        }

    def get_fb_title(self, **kwargs):
        # Circular imports
        from apps.projects.models import ProjectPlan
        
        try:
            plan = self.project.projectplan
            country = plan.country.name if plan.country else ''
        except ProjectPlan.DoesNotExist:
            country = ''
        return _(u"Share your skills: {task_name} in {country}").format(
                task_name = self.title,
                country = country
            )

    def get_tweet(self, **kwargs):
        # Circular imports
        from apps.projects.models import ProjectPlan
        
        """
        {URL} is replaced in Ember to fill in the page url, avoiding the
        need to provide front-end urls in our Django code.
        """
        
        try:
            plan = self.project.projectplan
            country = plan.country.name if plan.country else ''
        except ProjectPlan.DoesNotExist:
            country = ''

        request = kwargs.get('request')
        lang_code = request.LANGUAGE_CODE
        twitter_handle = settings.TWITTER_HANDLES.get(lang_code, settings.DEFAULT_TWITTER_HANDLE)
        
        expertise = self.skill.name if self.skill else ''
        expertise_hashtag = clean_for_hashtag(expertise)

        tweet = _(u"Share your skills: {task_name} in {country} {{URL}}"
                   " #{expertise} via @{twitter_handle}").format(
                    task_name = self.title,
                    country = country,
                    expertise = expertise_hashtag,
                    twitter_handle = twitter_handle
                )
        return tweet

    class Meta:
        ordering = ['-created']


class TaskMember(models.Model):

    class TaskMemberStatuses(DjangoChoices):
        applied = ChoiceItem('applied', label=_("Applied"))
        accepted = ChoiceItem('accepted', label=_("Accepted"))
        rejected = ChoiceItem('rejected', label=_("Rejected"))
        stopped = ChoiceItem('stopped', label=_("Stopped"))
        realized = ChoiceItem('realized', label=_("Realised"))

    task = models.ForeignKey('Task')
    member = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.CharField(_("status"), max_length=20, choices=TaskMemberStatuses.choices)

    motivation = models.TextField(_("Motivation"), help_text=_("Motivation by applicant."), blank=True)
    comment = models.TextField(_("Comment"), help_text=_("Comment by task owner."), blank=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))


class TaskFile(models.Model):

    task = models.ForeignKey('Task')
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=255)
    file = models.FileField(_("file"), upload_to='task_files/')
    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("Updated"))
