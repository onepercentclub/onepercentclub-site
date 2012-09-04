from django.db.models import Q, Count, Sum
from django.conf.urls.defaults import *
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.core.serializers import serialize,json
from django.utils import simplejson


from tastypie.resources import ModelResource, Resource
from tastypie import fields, utils
from tastypie.authorization import DjangoAuthorization
from tastypie.utils import trailing_slash
from tastypie.paginator import Paginator
from tastypie.serializers import Serializer
from sorl.thumbnail import get_thumbnail

from apps.media.models import EmbeddedVideo

from .models import Project, IdeaPhase, FundPhase, ActPhase, ResultsPhase, ProjectTheme

class PrettyJSONSerializer(Serializer):
   json_indent = 2
   
   def to_html(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        pre = simplejson.dumps(data, cls=json.DjangoJSONEncoder,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)

        return '<html><head></head><body><pre>%s</pre></body></html>' % pre


class ResourceBase(ModelResource):
    class Meta:
        authorization = DjangoAuthorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        serializer = PrettyJSONSerializer()
        always_return_data = True


class ProjectFilters(object):
    """ 
        Have a need way to gather all project filters so we can use
        it for the project filtering and the search form
    """
    # TODO: Code & use me
    pass


class ProjectPreviewResource(ResourceBase):
    """ Filter the projects """

    # Might want to use this later
    # However it does not work if the related Phase doesn't exist...
    #
    #    ideaphase = fields.OneToOneField(
    #                 'apps.projects.api.IdeaPhaseResource', 'ideaphase', full=True)
    #    fundphase = fields.OneToOneField(
    #                 'projects.api.FundPhaseResource', 'fundphase', full=False)
    #    actphase = fields.OneToOneField(
    #                'projects.api.ActPhaseResource', 'actphase', full=False)
    #    resultsphase = fields.OneToOneField(
    #                'projects.api.ResultsPhaseResource', 'resultsphase', full=False)
    

    def dehydrate(self, bundle):
        """ Add some more fields to project objects """
        bundle.data['location'] = {
                                   'country' : bundle.obj.country,
                                   'subregion' : bundle.obj.country.subregion,
                                   }
        bundle.data['money_donated'] = bundle.obj.money_donated()
        bundle.data['money_asked'] = bundle.obj.money_asked()
        bundle.data['money_needed'] = bundle.obj.money_needed()
        # TODO: move this to model
        try:
            bundle.data['thumbnail'] = '/static/media/' + unicode(
                                             get_thumbnail(bundle.obj.image,
                                            '230x150', crop='center', quality=85))
        except:
            bundle.data['thumbnail'] = 'http://placehold.it/230x150'

        return bundle

    class Meta(ResourceBase.Meta):
        queryset = Project.objects.all()
        detail_uri_name = 'slug'
        filtering = {
             "latitude": ('gte', 'lte'),
             "longitude": ('gte', 'lte'),
             "title": ('istartswith', 'icontains')
        }

    # Make sure we give resource uri's with slugs
    def dehydrate_resource_uri(self, bundle=None):
        return '/projects/api/project/' + bundle.obj.slug + '/'

    def filter_text(self, query):
        """ Custom filter for free text search. """
        query = query.replace('+', ' ')
        qset = (
                Q(title__icontains=query) |
                Q(actphase__description__icontains=query) |
                Q(fundphase__description__icontains=query) |
                Q(fundphase__description_long__icontains=query) |
                Q(fundphase__sustainability__icontains=query) |
                Q(fundphase__money_other_sources__icontains=query) |
                Q(fundphase__social_impact__icontains=query) |
                Q(fundphase__impact_group__icontains=query) |
                Q(slug__icontains=query)
                )
        return qset


    def apply_filters(self, request, applicable_filters):
        """ Apply custom filters """
        """ Get the objects with standard filters """
        filtered_objects = super(ProjectPreviewResource, self).apply_filters(request, applicable_filters)

        text = request.GET.get('text', None)
        if text:
            filtered_objects = filtered_objects.filter(self.filter_text(text))

        regions = request.GET.get('regions', None)
        if regions:
            filtered_objects = filtered_objects.filter(country__subregion__numeric_code__in=regions.split(','))

        countries = request.GET.get('countries', None)
        if countries:
            filtered_objects = filtered_objects.filter(country__numeric_code__in=countries.split(','))

        phases = request.GET.get('phases', None)
        if phases:
            filtered_objects = filtered_objects.filter(phase__in=phases.split(','))

        languages = request.GET.get('languages', None)
        if languages:
            filtered_objects = filtered_objects.filter(project_language__in=languages.split(','))

        themes = request.GET.get('themes', None)
        if themes:
            filtered_objects = filtered_objects.filter(themes__slug__in=themes.split(','))

        tags = request.GET.get('tags', None)
        if tags:
            filtered_objects = filtered_objects.filter(tags__slug__in=tags.split(','))

        order = request.GET.get('order', None)
        if order == 'alphabetically':
            filtered_objects = filtered_objects.order_by('title')
        if order == 'newest':
            filtered_objects = filtered_objects.order_by('-created')

        return filtered_objects.distinct()


class ProjectDetailResource(ProjectPreviewResource):
    def dehydrate(self, bundle):
        """ Add some more fields to project objects """
        bundle.data['location'] = {
                                   'country' : bundle.obj.country,
                                   'subregion' : bundle.obj.country.subregion,
                                   }
        bundle.data['money_donated'] = bundle.obj.money_donated()
        bundle.data['money_asked'] = bundle.obj.money_asked()
        bundle.data['money_needed'] = bundle.obj.money_needed()
        try:
            bundle.data['description'] = bundle.obj.ideaphase.description
        except IdeaPhase.DoesNotExist:
            bundle.data['description'] = ""
         
        try:
            ownerimage = '/static/media/' + unicode(
                                             get_thumbnail(bundle.obj.owner.userprofile.picture,
                                            '90x90', crop='center', quality=85))
        except:
            ownerimage = 'http://placehold.it/90x90'
        bundle.data['owner'] = {
                                'first_name': bundle.obj.owner.first_name,
                                'last_name': bundle.obj.owner.last_name,
                                'image': ownerimage
                                }
        
        if bundle.obj.phase in ['fund', 'act', 'results']:
            bundle.data['description'] = bundle.obj.fundphase.description
            bundle.data['description_long'] = bundle.obj.fundphase.description_long
            bundle.data['sustainability'] = bundle.obj.fundphase.sustainability
            bundle.data['social_impact'] = bundle.obj.fundphase.social_impact
        
        bundle.data['tags'] = list(bundle.obj.tags.values_list('name').all())
        bundle.data['themes'] = list(bundle.obj.themes.values_list('name').all());
        # TODO: move this to model
        try:
            bundle.data['thumbnail'] = '/static/media/' + unicode(
                                             get_thumbnail(bundle.obj.image,
                                            '225x150', crop='center', quality=85))
        except:
            bundle.data['thumbnail'] = 'http://placehold.it/225x150'
        try:
            bundle.data['picture'] = '/static/media/' + unicode(
                                             get_thumbnail(bundle.obj.image,
                                            '480x360', crop='center', quality=90))
        except:
            bundle.data['picture'] = 'http://placehold.it/480x360'
        
        video = EmbeddedVideo.objects.all().filter(album__in =bundle.obj.albums.all())[0:1];
        if video:
            bundle.data['video'] = video[0].thumbnail_url
        return bundle

    class Meta(ResourceBase.Meta):
        detail_uri_name = 'slug'
        queryset = Project.objects.all()
        filtering = {
             "latitude": ('gte', 'lte'),
             "longitude": ('gte', 'lte'),
             "title": ('istartswith', 'icontains')
        }

    # Make sure we give resource uri's with slugs
    def dehydrate_resource_uri(self, bundle=None):
        return '/projects/api/projectdetail/' + bundle.obj.slug + '/'




class SearchFormElement(object):
    """  
        Use this to create Elements for a search form.
        
        Example:
        text = SearchFormElement()
        text.title = 'Text Search'
        text.type = 'text'
        text.name = 'text'
        dict = text.compose()
    """
        
    # TODO: Make sure kwargs works
    def __init__(self, **kwargs):
        for key,value in kwargs:
            self.key = value
    
    # TODO: give a 'selected' for selected options and return
    #       value for filled out input boxes
    # TODO: Nice exceptions if obligatory fields aren't set
    def compose(self):
        """ compose the dict for this element """
        if self.type in ['select', 'radio', 'checkbox']:
            qs = self.queryset
            if hasattr(self, 'option_value') == False:
                self.option_value = self.option_title
            qs = qs.values_list(self.option_title, self.option_value)
            if hasattr(self, 'order'):
                qs = qs.order_by(self.order)
            qs = qs.annotate(count=Count('slug'))
            if hasattr(self, 'limit'):
                qs = qs[0:self.limit]
            opts = list(qs)
            options = []
            for opt in opts:
                options.append({
                         'name': opt[0], 
                         'id': opt[1],
                         'count': opt[2] 
                         })
            element = {
                        'title': self.title,
                        'name': self.name,
                        'type': self.type,
                        'options': options,
                      }
        else:
            element = {
                        'title': self.title,
                        'name': self.name,
                        'type': self.type
                      }
        return element


class ProjectSearchFormResource(Resource):
    """
        Have a separate resource for Search Form
        We want to keep track of the number of projects per option
    """

    def filter_text(self, query):
        """ Custom filter for free text search. """
        query = query.replace('+', ' ')
        qset = (
                Q(title__icontains=query) |
                Q(actphase__description__icontains=query) |
                Q(fundphase__description__icontains=query) |
                Q(fundphase__description_long__icontains=query) |
                Q(fundphase__sustainability__icontains=query) |
                Q(fundphase__money_other_sources__icontains=query) |
                Q(fundphase__social_impact__icontains=query) |
                Q(fundphase__impact_group__icontains=query) |
                Q(slug__icontains=query)
                )
        return qset


    # TODO: put filters somewhere else
    # TODO: Don't reference GET directly here!
    def custom_filters(self, request, filtered_objects, skip = None):
        """ Use the same filters for this as for Project Search for now """
        text = request.GET.get('text', None)
        if text:
            filtered_objects = filtered_objects.filter(self.filter_text(text))

        phases = request.GET.get('phases', None)
        if phases and skip != 'phases':
            filtered_objects = filtered_objects.filter(phase__in=phases.split(','))

        regions = request.GET.get('regions', None)
        if regions and skip != 'regions':
            filtered_objects = filtered_objects.filter(country__subregion__numeric_code__in=regions.split(','))

        countries = request.GET.get('countries', None)
        if countries and skip != 'countries':
            filtered_objects = filtered_objects.filter(country__numeric_code__in=countries.split(','))

        languages = request.GET.get('languages', None)
        if languages and skip != 'languages':
            filtered_objects = filtered_objects.filter(project_language__in=languages.split(','))

        themes = request.GET.get('themes', None)
        if themes and skip != 'themes': 
            filtered_objects = filtered_objects.filter(themes__slug__in=themes.split(','))

        tags = request.GET.get('tags', None)
        if tags and skip != 'tags':
            filtered_objects = filtered_objects.filter(tags__slug__in=tags.split(','))

        order = request.GET.get('order', None)
        if order == 'alphabetically':
            filtered_objects = filtered_objects.order_by('title')
        if order == 'newest':
            filtered_objects = filtered_objects.order_by('-created')

        return filtered_objects
    

    def dehydrate(self, bundle):
        """ Use the form elements as objects """
        bundle = bundle.obj
        return bundle

    def obj_get_list(self, request):
        """ 
            Objects for this API call will be form elements (formfileds).
            Let's create some form elements!
        """
        
        #projects = self.custom_filters(request, Project.objects)

        text = SearchFormElement()
        text.title = 'Text Search'
        text.type = 'text'
        text.name = 'text'

        phases = SearchFormElement()
        phases.queryset = self.custom_filters(request, Project.objects, 'phases')
        phases.title = 'Project Phase'
        phases.type = 'checkbox'
        phases.name = 'phases'
        phases.option_title = 'phase'
        phases.order = 'phase'
        

        countries = SearchFormElement()
        countries.queryset = self.custom_filters(request, Project.objects, 'countries')
        countries.title = 'Country'
        countries.type = 'select'
        countries.name = 'countries'
        countries.option_title = 'country__name'
        countries.option_value = 'country__numeric_code'
        countries.order = 'country'

        regions = SearchFormElement()
        regions.queryset = self.custom_filters(request, Project.objects, 'regions')
        regions.title = 'Regions'
        regions.type = 'select'
        regions.name = 'regions'
        regions.option_title = 'country__subregion__name'
        regions.option_value = 'country__subregion__numeric_code'
        regions.order = 'country__subregion'

        themes = SearchFormElement()
        themes.queryset = self.custom_filters(request, Project.objects, 'themes').filter(themes__isnull=False)
        themes.title = 'Themes'
        themes.type = 'checkbox'
        themes.name = 'themes'
        themes.option_title = 'themes__name'
        themes.option_value = 'themes__slug'
        themes.order = 'themes'

        tags = SearchFormElement()
        tags.queryset =  self.custom_filters(request, Project.objects, 'tags').filter(tags__isnull=False)
        tags.title = 'Tags'
        tags.type = 'checkbox'
        tags.name = 'tags'
        tags.option_title = 'tags__name'
        tags.option_value = 'tags__slug'
        tags.order = '-count'
        tags.limit = 12

        items = [text.compose(), phases.compose(), regions.compose(), countries.compose(), tags.compose(), themes.compose()]
           
        return items


    class Meta(ResourceBase.Meta):
        limit = 0

class IdeaPhaseResource(ResourceBase):
    project = fields.OneToOneField(ProjectPreviewResource, 'project')

    class Meta:
        queryset = IdeaPhase.objects.select_related('IdeaPhase').all()


class FundPhaseResource(ResourceBase):
    project = fields.OneToOneField(ProjectPreviewResource, 'project')

    class Meta:
        queryset = FundPhase.objects.all()


class ActPhaseResource(ResourceBase):
    project = fields.OneToOneField(ProjectPreviewResource, 'project')

    class Meta:
        queryset = ActPhase.objects.all()


class ResultsPhaseResource(ResourceBase):
    project = fields.OneToOneField(ProjectPreviewResource, 'project')

    class Meta:
        queryset = ResultsPhase.objects.all()


