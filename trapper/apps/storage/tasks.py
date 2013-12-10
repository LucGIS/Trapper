from __future__ import absolute_import

from celery import shared_task

from trapper.apps.storage.models import CollectionUploadJob
from trapper.tools.batch_uploading import ResourceArchiveValidator, ResourceArchiveUploader

@shared_task
def process_collection_upload(job_pk):
	job = CollectionUploadJob.objects.get(pk=job_pk)
	job.set_status(CollectionUploadJob.STATUS_PENDING)

	if not job.definition or not job.archive:
		job.resolve_as_error("Definition file of archive file are missing")
		return

	v = ResourceArchiveValidator(job.definition, job.archive, job.owner)
	error = v.check_errors()
	if error:
		job.resolve_as_error(error)
		return
	
	u = ResourceArchiveUploader(job.definition, job.archive, job.owner)
	error = u.upload_collections()
	if error:
		job.resolve_as_error(error)
		return
	else:
		job.resolve_as_ok()
