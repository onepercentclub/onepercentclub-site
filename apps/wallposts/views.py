import django_filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.wallposts.models import TextWallPost, MediaWallPost, MediaWallPostPhoto
from apps.wallposts.permissions import IsConnectedWallPostAuthorOrReadOnly
from apps.wallposts.serializers import TextWallPostSerializer, MediaWallPostSerializer, MediaWallPostPhotoSerializer
from bluebottle.bluebottle_drf2.permissions import IsAuthorOrReadOnly, AllowNone
from bluebottle.bluebottle_utils.utils import set_author_editor_ip, get_client_ip
from rest_framework import permissions
from bluebottle.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView, ListAPIView
from apps.projects.models import Project
from .models import WallPost, Reaction
from .serializers import ReactionSerializer, WallPostSerializer


class WallPostFilter(django_filters.FilterSet):
    parent_type = django_filters.CharFilter(name="content_type__name")
    parent_id = django_filters.NumberFilter(name="object_id")

    class Meta:
        model = WallPost
        fields = ['parent_type', 'parent_id']


class WallPostList(ListAPIView):
    model = WallPost
    serializer_class = WallPostSerializer
    filter_class = WallPostFilter
    paginate_by = 5

    def get_queryset(self):
        queryset = super(WallPostList, self).get_queryset()

        # Some custom filtering projects slugs.
        parent_type = self.request.QUERY_PARAMS.get('parent_type', None)
        parent_id = self.request.QUERY_PARAMS.get('parent_id', None)
        if parent_type == 'project' and parent_id:
            try:
                project = Project.objects.get(slug=parent_id)
            except Project.DoesNotExist:
                return WallPost.objects.none()
            queryset = queryset.filter(object_id=project.id)

        queryset = queryset.order_by('-created')
        return queryset


class TextWallPostList(ListCreateAPIView):
    model = TextWallPost
    serializer_class = TextWallPostSerializer
    filter_class = WallPostFilter
    paginate_by = 5
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        queryset = super(TextWallPostList, self).get_queryset()

        # Some custom filtering projects slugs.
        parent_type = self.request.QUERY_PARAMS.get('parent_type', None)
        parent_id = self.request.QUERY_PARAMS.get('parent_id', None)
        if parent_type == 'project' and parent_id:
            try:
                project = Project.objects.get(slug=parent_id)
            except Project.DoesNotExist:
                return WallPost.objects.none()
            queryset = queryset.filter(object_id=project.id)

        queryset = queryset.order_by('-created')
        return queryset

    def pre_save(self, obj):
        if not obj.author:
            obj.author = self.request.user
        else:
            obj.editor = self.request.user
        obj.ip_address = get_client_ip(self.request)


class MediaWallPostList(TextWallPostList):
    model = MediaWallPost
    serializer_class = MediaWallPostSerializer
    filter_class = WallPostFilter
    paginate_by = 5


class WallPostDetail(RetrieveUpdateDeleteAPIView):
    model = WallPost
    serializer_class = WallPostSerializer
    permission_classes = (IsAuthorOrReadOnly, )


class MediaWallPostPhotoList(ListCreateAPIView):
    model = MediaWallPostPhoto
    serializer_class = MediaWallPostPhotoSerializer
    paginate_by = 4

    def pre_save(self, obj):
        if not obj.author:
            obj.author = self.request.user
        else:
            obj.editor = self.request.user
        obj.ip_address = get_client_ip(self.request)

    def create(self, request, *args, **kwargs): #FIXME
        """
        Work around browser issues.

        Adding photos to a wallpost works correctly in Chrome. Firefox (at least
        FF 24) sends the ```mediawallpost``` value to Django with the value
        'null', which is then interpreted as a string in Django. This is
        incorrect behaviour, as ```mediawallpost``` is a relation.

        Eventually, this leads to HTTP400 errors, effectively breaking photo
        uploads in FF.

        The quick fix is detecting this incorrect 'null' string in ```request.POST```
        and setting it to an empty string. ```request.POST``` is mutable because
        of the multipart nature.

        NOTE: This is something that should be fixed in the Ember app or maybe even
        Ember itself.
        """
        post = request.POST.get('mediawallpost', False)
        if post and post == u'null':
            request.POST['mediawallpost'] = u''
        return super(MediaWallPostPhotoList, self).create(request, *args, **kwargs)


class MediaWallPostPhotoDetail(RetrieveUpdateDeleteAPIView):
    model = MediaWallPostPhoto
    serializer_class = MediaWallPostPhotoSerializer
    permission_classes = (IsAuthorOrReadOnly, IsConnectedWallPostAuthorOrReadOnly)


class ReactionList(ListCreateAPIView):
    model = Reaction
    serializer_class = ReactionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 10
    filter_fields = ('wallpost',)

    def pre_save(self, obj):
        set_author_editor_ip(self.request, obj)


class ReactionDetail(RetrieveUpdateDeleteAPIView):
    model = Reaction
    serializer_class = ReactionSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def pre_save(self, obj):
        set_author_editor_ip(self.request, obj)
