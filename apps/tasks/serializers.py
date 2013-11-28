from bluebottle.bluebottle_drf2.serializers import PrimaryKeyGenericRelatedField, TagSerializer, FileSerializer, TaggableSerializerMixin
from bluebottle.accounts.serializers import UserPreviewSerializer
from bluebottle.bluebottle_utils.serializers import MetaField


from apps.projects.serializers import ProjectPreviewSerializer
from apps.tasks.models import Task, TaskMember, TaskFile, Skill
from apps.wallposts.serializers import TextWallPostSerializer, WallPostListSerializer
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.encoding import smart_text
from rest_framework import serializers


class TaskPreviewSerializer(serializers.ModelSerializer):
    author = UserPreviewSerializer()
    project = ProjectPreviewSerializer()
    skill = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'location', 'skill', 'status', 'created', 'project', 'deadline', 'time_needed')


class TaskMemberSerializer(serializers.ModelSerializer):
    member = UserPreviewSerializer()
    task = serializers.PrimaryKeyRelatedField()
    status = serializers.ChoiceField(choices=TaskMember.TaskMemberStatuses.choices, required=False, default=TaskMember.TaskMemberStatuses.applied)
    motivation = serializers.CharField(required=False)

    class Meta:
        model = TaskMember
        fields = ('id', 'member', 'task', 'status', 'created', 'motivation')


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
    skill = serializers.PrimaryKeyRelatedField()
    author = UserPreviewSerializer()

    tags = TagSerializer()
    meta_data = MetaField(
        title = 'get_meta_title', 
        fb_title = 'get_fb_title',
        tweet = 'get_tweet',
        image_source = 'project__projectplan__image',
        )

    class Meta:
        model = Task
        fields = ('id', 'title', 'project', 'description', 'end_goal', 'members', 'files', 'location', 'skill',
                  'time_needed', 'author', 'status', 'created', 'deadline', 'tags', 'meta_data')


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


