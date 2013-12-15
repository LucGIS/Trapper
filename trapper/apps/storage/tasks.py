############################################################################
#   Copyright (c) 2013  IBS PAN Bialowieza                                 #
#   Copyright (c) 2013  Bialystok University of Technology                 #
#                                                                          #
#   This file is a part of Trapper.                                        #
#                                                                          #
#   Trapper is free software; you can redistribute it and/or modify        #
#   it under the terms of the GNU General Public License as published by   #
#   the Free Software Foundation; either version 2 of the License, or      #
#   (at your option) any later version.                                    #
#                                                                          #
#   This program is distributed in the hope that it will be useful,        #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#   GNU General Public License for more details.                           #
#                                                                          #
#   You should have received a copy of the GNU General Public License      #
#   along with this program; if not, write to the                          #
#   Free Software Foundation, Inc.,                                        #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.              #
############################################################################

from __future__ import absolute_import

from celery import shared_task

from trapper.apps.storage.models import CollectionUploadJob
from trapper.tools.batch_uploading import ResourceArchiveValidator, ResourceArchiveUploader

@shared_task
def process_collection_upload(job_pk):
	"""Performs a final validation and uploads the collection.

	:param job_pk: Primary key of the job to process.
	:type job_pk: int
	:returns: A bar
	:rtype: int
	"""

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
