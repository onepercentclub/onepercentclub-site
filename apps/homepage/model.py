from apps.banners.models import Slide
from apps.projects.models import Project
from apps.quotes.models import Quote
from apps.statistics.models import Statistic


# Instead of serving all the objects separately we combine Slide, Quote and Stats into a dummy object

class HomePage(object):

    def get(self, language):
        self.id = 1
        self.quotes= Quote.objects.published().filter(language=language)
        self.slides = Slide.objects.published().filter(language=language)
        self.stats = Statistic.objects.order_by('-creation_date').all()[0]
        self.projects = Project.objects.filter(phase='campaign').order_by('?')[0:4]

        return self