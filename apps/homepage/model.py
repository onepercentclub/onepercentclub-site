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
        stats = Statistic.objects.order_by('-creation_date').all()
        if len(stats) > 0:
            self.stats = stats[0]
        else:
            self.stats = None
        projects = Project.objects.filter(phase='campaign').order_by('?')
        if len(projects) > 4:
            self.projects = projects[0:4]
        elif len(projects) > 0:
            self.projects = projects[0:len(projects)]
        else:
            self.projects = None
        return self