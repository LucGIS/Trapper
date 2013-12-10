import yaml
import zipfile
import os
from StringIO import StringIO

from django.core.files import File
from django.contrib.auth.models import User

from trapper.apps.geomap.models import Location
from trapper.apps.storage.models import Resource, Collection
from trapper.apps.media_classification.models import Project, ProjectCollection

class YAMLReader:
	"""
	Reads the YAML file and rewinds the source file for later use
	"""

	def read_yaml_file(self):
		try:
			yaml_dict = yaml.load(self.yaml_file)
			self.yaml_file.seek(0)
			return yaml_dict
		except:
			return None

class ConfigFileValidator(YAMLReader):
	"""
	Validator for the batch uploading configuration files.
	Checks mainly for the valid syntax of the YAML file,
	and some basic DB objects and privileges.
	"""

	def __init__(self, yaml_file, user):
		self.yaml_file = yaml_file
		self.user = user

	def check_errors(self):
		"""
		Checks for possible errors within configuration file and the zipfile.
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

			if 'managers' in col:
				for m in col['managers']:
					for _, username in m.iteritems():
						try:
							User.objects.get(username=username)
						except:
							return "One or more managers does not exist: '%s'" % (username,)


		return None

class ResourceArchiveValidator(YAMLReader):
	"""
	Validator for the archive file.
	Checks whether definition file describes the archive properly.
	"""

	def __init__(self, yaml_file, zip_archive, user):
		self.yaml_file = yaml_file
		self.zip_archive = zip_archive
		self.user = user


	def check_errors(self):
		"""
		Checks for possible errors within configuration file and the zipfile
		"""

		self.yaml_dict = self.read_yaml_file()
		if not self.yaml_dict:
			return "Error opening configuration file. YAML syntax might be invalid."

		archive_errors = self.invalid_archive()
		if archive_errors:
			return archive_errors

		matching_errors = self.invalid_matching()
		if matching_errors:
			return matching_errors

		return None

	def invalid_archive(self):
		"""
		Checks whether the archive file has the correct structure.
		"""
		return None

	def invalid_matching(self):
		"""
		Checks whether definition file matches the archive
		"""
		archive = zipfile.ZipFile(self.zip_archive)
		cfg = self.yaml_dict
		for c in cfg['collections']:
			dir = os.path.join(c['resources_dir'],'')
			if dir not in archive.namelist():
				return "Directory '%s' was not found in the archive file" % (dir,)
		return None

class ResourceArchiveUploader(YAMLReader):
	"""
	Uploads the resources in archive as well as creates the necessary collections.
	"""
	RESOURCE_SUBDIRS = (
		('webm', 'video/webm'),
		('mp4', 'video/mp4'),
		('jpg', 'image/jpeg'),
	)

	# Extesion which will be uploaded to the Resource.file field
	FILE_EXTENSIONS = ('.mp4', '.jpg',)

	# Extesion which will be uploaded to the Resource.extra_file field
	FILE_EXTRA_EXTENSIONS = ('.webm',)

	EXTENSIONS = FILE_EXTENSIONS + FILE_EXTRA_EXTENSIONS

	def __init__(self, yaml_file, zip_archive, user):
		self.yaml_file = yaml_file
		self.zip_archive = zip_archive
		self.user = user
	
	def upload_collections(self):
		"""
		Checks whether definition file matches the archive
		"""

		cfg = self.read_yaml_file()
		archive = zipfile.ZipFile(self.zip_archive)
		resource_names = []
		for c in cfg['collections']:
			dir = os.path.join(c['resources_dir'],'')
			for subdir, mime in self.RESOURCE_SUBDIRS:
				dir2 = os.path.join(dir, subdir)
				resources = [name for name in archive.namelist() if name.startswith(dir2)]
				for r in resources:
					directory, file_name = os.path.split(r)
					raw_name, extension = os.path.splitext(file_name)
					if extension.lower() in self.EXTENSIONS:
						resource_names.append(r)

		resource_names = list(set(resource_names))
		resource_objects = {}
		for r in resource_names:
			directory, file_name = os.path.split(r)
			raw_name, extension = os.path.splitext(file_name)
			if extension.lower() in self.EXTENSIONS:
				bin_data = archive.read(r)
				f2 = StringIO()
				f2.write(bin_data)
				f2.seek(0)
				if raw_name in resource_objects:
					res_obj = resource_objects[raw_name]
				else:
					res_obj = Resource(name=raw_name, uploader=self.user, owner=self.user)
					resource_objects[raw_name] = res_obj
				if extension.lower() in self.FILE_EXTENSIONS:
					res_obj.file.save(file_name, File(f2), save=False)
				elif extension.lower() in self.FILE_EXTRA_EXTENSIONS:
					res_obj.extra_file.save(file_name, File(f2), save=False)

		for name, obj in resource_objects.iteritems():
			print name
			obj.update_metadata(commit=True)

		for c in cfg['collections']:
			dir = os.path.join(c['resources_dir'],'')
			res_list = [name for name in resource_names if name.startswith(dir)]
			res_list = [resource_objects[os.path.splitext(os.path.split(name)[1])[0]] for name in res_list]
			col_obj = Collection.objects.create(name=c['name'], owner=self.user)
			col_obj.resources.add(*res_list)

			# Add managers to collection
			if 'managers' in c:
				for m in c['managers']:
					col_obj.managers.add(User.objects.get(username=m['username']))

			# Set up locations
			if 'location_id' in c:
				for res in res_list:
					res.location = Location.objects.get(location_id=c['location_id'])
					res.save()

			# Add to media classification project
			if 'project_id' in c:
				p = Project.objects.get(pk=int(c['project_id']))
				ProjectCollection.objects.create(project=p, collection=col_obj, active=True, cs_enabled=False)
		return None
