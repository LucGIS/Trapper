from easy_thumbnails.files import get_thumbnailer
from trapper.apps import storage
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate missing thumbnails'
                    
    def handle(self, *args, **options):
        resources = storage.models.Resource.objects.all()
        count = len(resources)
        errors = []
        self.stdout.write("Generating thumbnails for (%s) resources..." % count)
        aliases = settings.THUMBNAIL_ALIASES['']
        for resource in resources:
            count = count - 1
            self.stdout.write("Processing file %s (%s remaining)" % (resource.file.file.name, count))
            try:
                thumbnailer = get_thumbnailer(resource.file)
                for key in aliases.keys():
                    thumbnailer.get_thumbnail(aliases[key])
            except Exception as e:
                errors.append((resource.file.file.name, e))
        print "\nERRORS:\n"
        for error in errors: 
            print "FILE: %s " % error[0]
            print "ERROR: %s" % error[1]
            print
        
