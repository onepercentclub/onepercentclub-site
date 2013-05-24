from apps.tasks.models import Task, TaskMember, TaskFile
from django.contrib import admin
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.models import ModelChoiceField


class TaskMemberForm(ModelForm):
    member = ModelChoiceField(queryset=User.objects.order_by('username'))

    class Meta:
        model = TaskMember


class TaskMemberAdminInline(admin.StackedInline):
    model = TaskMember
    form = TaskMemberForm

    readonly_fields = ('created', )
    fields =  readonly_fields + ('member', 'status')
    extra = 1


class TaskFileForm(ModelForm):
    author = ModelChoiceField(queryset=User.objects.order_by('username'))

    class Meta:
        model = TaskFile


class TaskFileAdminInline(admin.StackedInline):
    model = TaskFile

    readonly_fields = ('created', )
    fields =  readonly_fields + ('author', 'file')
    extra = 1


class TaskForm(ModelForm):
    owner = ModelChoiceField(queryset=User.objects.order_by('username'))

    class Meta:
        model = Task


class TaskAdmin(admin.ModelAdmin):

    date_hierarchy = 'created'

    inlines = (TaskMemberAdminInline, TaskFileAdminInline, )

    list_filter = ('status', )
    list_display = ('title', 'project', 'status')

    search_fields = (
        'title', 'description',
        'author__first_name', 'author__last_name'
    )
admin.site.register(Task, TaskAdmin)
