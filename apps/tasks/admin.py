from bluebottle.accounts.models import BlueBottleUser
from apps.tasks.models import Task, TaskMember, TaskFile, Skill
from django.contrib import admin
from django.forms import ModelForm
from django.forms.models import ModelChoiceField


class TaskMemberAdminInline(admin.StackedInline):
    model = TaskMember

    raw_id_fields = ('member', )
    readonly_fields = ('created', )
    fields =  readonly_fields + ('member', 'status', 'motivation')
    extra = 0



class TaskFileAdminInline(admin.StackedInline):
    model = TaskFile

    raw_id_fields = ('author', )
    readonly_fields = ('created', )
    fields =  readonly_fields + ('author', 'file')
    extra = 0


class TaskForm(ModelForm):
    owner = ModelChoiceField(queryset=BlueBottleUser.objects.order_by('email'))

    class Meta:
        model = Task


class TaskAdmin(admin.ModelAdmin):

    date_hierarchy = 'created'

    inlines = (TaskMemberAdminInline, TaskFileAdminInline, )

    raw_id_fields = ('author', 'project')
    list_filter = ('status', )
    list_display = ('title', 'project', 'status', 'date_status_change')

    readonly_fields = ('date_status_change',)

    search_fields = (
        'title', 'description',
        'author__first_name', 'author__last_name'
    )
    # ordering
    fields = (
        'title', 'description', 'end_goal', 'location',
        'expertise', 'skill', 'time_needed',
        'status', 'date_status_change',
        'people_needed',
        'project', 'author',
        'tags',
        'deadline',
    )

admin.site.register(Task, TaskAdmin)


class SkillAdmin(admin.ModelAdmin):
    model=Skill

admin.site.register(Skill, SkillAdmin)
