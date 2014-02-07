from bluebottle.tasks.serializers import TaskSerializer

class OnepercentTaskSerializer(TaskSerializer):


    class Meta:
        model = TaskSerializer.Meta.model
        fields = TaskSerializer.Meta.fields + ()