from apps.tasks.models import Task, TaskMember, TaskFile
from django.contrib import admin
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.models import ModelChoiceField


class TaskMemberAdminInline(admin.StackedInline):
    model = TaskMember

    raw_id_fields = ('member', )
    readonly_fields = ('created', )
    fields =  readonly_fields + ('member', 'status')
    extra = 1



class TaskFileAdminInline(admin.StackedInline):
    model = TaskFile

    raw_id_fields = ('author', )
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

    raw_id_fields = ('author', )
    list_filter = ('status', )
    list_display = ('title', 'project', 'status')

    search_fields = (
        'title', 'description',
        'author__first_name', 'author__last_name'
    )
admin.site.register(Task, TaskAdmin)
