from apps.bluebottle_drf2.serializers import PrimaryKeyGenericRelatedField, TaggableSerializerMixin, TagSerializer, FileSerializer
from apps.accounts.serializers import UserPreviewSerializer
from apps.tasks.models import Task, TaskMember, TaskFile
from apps.wallposts.serializers import TextWallPostSerializer, WallPostListSerializer
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


class TaskPreviewSerializer(serializers.ModelSerializer):
    author = UserPreviewSerializer()

    class Meta:
        model = Task
        fields = ('id', 'title', 'location', 'expertise', 'status', 'created')


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
    members = TaskMemberSerializer(many=True, source='taskmember_set')
    files = TaskFileSerializer(many=True, source='taskfile_set')
    project = serializers.SlugRelatedField(slug_field='slug')
    author = UserPreviewSerializer()

    tags = TagSerializer()
    wallpost_ids = WallPostListSerializer()


    class Meta:
        model = Task
        fields = ('id', 'title', 'project', 'description', 'end_goal', 'members', 'files', 'location', 'expertise',
                  'time_needed', 'author', 'status', 'created', 'deadline', 'tags', 'wallpost_ids')


# Task WallPost serializers

class TaskWallPostSerializer(TextWallPostSerializer):
    """ TextWallPostSerializer with task specific customizations. """

    url = serializers.HyperlinkedIdentityField(view_name='task-twallpost-detail')
    task = PrimaryKeyGenericRelatedField(to_model=Task)

    class Meta(TextWallPostSerializer.Meta):
        # Add the project slug field.
        fields = TextWallPostSerializer.Meta.fields + ('task', )

    def save(self):
        # Save the project content type on save.
        task_type = ContentType.objects.get_for_model(Task)
        self.object.content_type_id = task_type.id
        return super(TaskWallPostSerializer, self).save()

