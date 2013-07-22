from apps.bluebottle_drf2.serializers import PrimaryKeyGenericRelatedField, TagSerializer, FileSerializer, TaggableSerializerMixin
from apps.accounts.serializers import UserPreviewSerializer
from apps.projects.serializers import ProjectPreviewSerializer
from apps.tasks.models import Task, TaskMember, TaskFile, Skill
from apps.wallposts.serializers import TextWallPostSerializer, WallPostListSerializer
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.encoding import smart_text
from rest_framework import serializers


class SkillField(serializers.SlugRelatedField):

    def __init__(self, *args, **kwargs):
        if not hasattr(kwargs, 'slug_field'):
            kwargs['slug_field'] = 'name'
        super(SkillField, self).__init__(*args, **kwargs)

    def from_native(self, data):
        if self.queryset is None:
            raise Exception('Writable related fields must include a `queryset` argument')

        try:
            return self.queryset.get(**{'id': data})
        except ObjectDoesNotExist:
            raise ValidationError(self.error_messages['does_not_exist'] %
                                  ('id', smart_text(data)))
        except (TypeError, ValueError):
            msg = self.error_messages['invalid']
            raise ValidationError(msg)


class TaskPreviewSerializer(serializers.ModelSerializer):
    author = UserPreviewSerializer()
    project = ProjectPreviewSerializer()
    skill = SkillField()

    class Meta:
        model = Task
        fields = ('id', 'title', 'location', 'skill', 'status', 'created', 'project', 'deadline', 'time_needed')


class TaskMemberSerializer(serializers.ModelSerializer):
    member = UserPreviewSerializer()
    task = serializers.PrimaryKeyRelatedField()
    status = serializers.ChoiceField(choices=TaskMember.TaskMemberStatuses.choices, required=False, default=TaskMember.TaskMemberStatuses.applied)

    class Meta:
        model = TaskMember
        fields = ('id', 'member', 'task', 'status', 'created')


class TaskFileSerializer(serializers.ModelSerializer):
    author = UserPreviewSerializer()
    task = serializers.PrimaryKeyRelatedField()
    file = FileSerializer()

    class Meta:
        model = TaskFile
        fields = ('id', 'author', 'task', 'file', 'created', 'title')


class TaskSerializer(TaggableSerializerMixin, serializers.ModelSerializer):
    members = TaskMemberSerializer(many=True, source='taskmember_set', required=False)
    files = TaskFileSerializer(many=True, source='taskfile_set', required=False)
    project = serializers.SlugRelatedField(slug_field='slug')
    skill = SkillField()

    author = UserPreviewSerializer()

    tags = TagSerializer()
    wallpost_ids = WallPostListSerializer()


    class Meta:
        model = Task
        fields = ('id', 'title', 'project', 'description', 'end_goal', 'members', 'files', 'location', 'skill',
                  'time_needed', 'author', 'status', 'created', 'deadline', 'tags', 'wallpost_ids')


class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = ('id', 'name')


# Task WallPost serializers

class TaskWallPostSerializer(TextWallPostSerializer):
    """ TextWallPostSerializer with task specific customizations. """

    url = serializers.HyperlinkedIdentityField(view_name='task-twallpost-detail')
    task = PrimaryKeyGenericRelatedField(Task)

    class Meta(TextWallPostSerializer.Meta):
        # Add the project slug field.
        fields = TextWallPostSerializer.Meta.fields + ('task', )


