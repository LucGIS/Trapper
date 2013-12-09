import yaml

from django.contrib.auth.models import User

from trapper.apps.geomap.models import Location
from trapper.apps.media_classification.models import Project

class ConfigFileValidator:
	"""
	Validator for the batch uploading configuration files.
	"""

	def __init__(self, yaml_file, user):
		self.yaml_file = yaml_file
		self.user = user

	def check_errors(self):
		"""
		Checks for possible errors within configuration file and the zipfile
		"""

		self.yaml_dict = self.read_yaml_file()
		if not self.yaml_dict:
			return "Error opening configuration file. YAML syntax might be invalid."

		definition_error = self.invalid_definition()
		if definition_error:
			return definition_error

		db_error = self.db_error()
		if db_error:
			return db_error

		return None

	def read_yaml_file(self):
		try:
			return yaml.load(self.yaml_file)
		except:
			return None
	
	def invalid_definition(self):
		"""
		First step validation.
		Checks whether provided configuration file contains a valid definition of collections
		"""
		ALLOWED_COLLECTION_KEYS = ['name', 'resources_dir', 'location_id', 'project_id', 'managers',]
		MANDATORY_COLLECTION_KEYS = ['name', 'resources_dir',]
	
		if len(self.yaml_dict) != 1 or self.yaml_dict.keys()[0] != 'collections':
			return "Configuration file must contain only one topmost key named 'collections'"
	
		for c in self.yaml_dict['collections']:
			for k,v in c.iteritems():
				if k not in ALLOWED_COLLECTION_KEYS:
					return "One or more collections contained an illegal key: '%s'" % (k,)
			for k in MANDATORY_COLLECTION_KEYS:
				if k not in c.keys():
					return "One or more mandatory keys was not found in the collection: '%s'" % (k,)
	
			# Checks whether all "managers" lists contain just a single "username" keyword
			if 'managers' in c:
				for m in c['managers']:
					for k,v in m.iteritems():
						if k != 'username':
							return "One or more managers' list items contains an illegal keyword: '%s'" % (k,)

			# Checks whether "project_id" is an integer
			if 'project_id' in c:
				try:
					int(c['project_id'])
				except:
					return "Value of key 'project_id' must an integer"
		return None
		
	def db_error(self):
		for col in self.yaml_dict['collections']:
			if 'location_id' in col:
				try:
					l = Location.objects.get(location_id=col['location_id'])
				except:
					return "Location '%s' does not exist" % (col['location_id'])
				if not l.can_view(self.user):
					return "You (%s) don't have a permission to use the location '%s'" % (self.user, l.pk)

			if 'project_id' in col:
				try:
					# TODO: use Slug field instead
					p = Project.objects.get(pk=col['project_id'])
				except:
					return "Project with ID '%s' does not exist" % (col['project_id'])
				if not p.can_edit(self.user):
					return "You (%s) don't have a permission to alter the project with ID=%s" % (self.user, p.pk)
		return None
