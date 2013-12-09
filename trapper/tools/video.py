import sys, os

def convert_avi(input_file, output_file, ffmpeg_exec="ffmpeg"):
	"""
	Converts the video to a lightweight format
	"""

	ffmpeg = '{ffmpeg} -y -i "{infile}" "{outfile}"'.format(
		ffmpeg=ffmpeg_exec,
		infile=input_file,
		outfile=output_file
	)

	output = "Source: %s\n" % input_file
	output += "Target: %s\n" % output_file
	output += "Command: %s\n" % ffmpeg

	f = os.popen(ffmpeg)
	ffmpegresult = f.readline()
	output += ffmpegresult

	#s = os.stat(output_file)
	#fsize = s.st_size

	return output

def convert_avi_to_webm(input_file, output_file, ffmpeg_exec="ffmpeg"):
	return convert_avi(input_file, output_file, ffmpeg_exec="ffmpeg")

def convert_avi_to_mp4(input_file, output_file, ffmpeg_exec="ffmpeg"):
	return convert_avi(input_file, output_file, ffmpeg_exec="ffmpeg")

def convert_batch(argv):
	"""
	Converts several video resources in a batch
	"""
	tmp_dir = argv[0]
	tmp_dir_webm = os.path.join(tmp_dir, "webm")
	tmp_dir_mp4 = os.path.join(tmp_dir, "mp4")

	input_files = argv[1:]
	if not os.path.exists(tmp_dir):
		print "Sorry, you must create the directory for the output files first"
		exit(1)

	if not os.path.exists(tmp_dir_webm):
		os.makedirs(tmp_dir_webm)

	if not os.path.exists(tmp_dir_mp4):
		os.makedirs(tmp_dir_mp4)

	for f in input_files:
		directory, file_name = os.path.split(f)
		raw_name, extension = os.path.splitext(file_name)
		print "Converting ", f
		convert_avi_to_mp4(f, os.path.join(tmp_dir, "mp4", raw_name + ".mp4"))
		convert_avi_to_webm(f, os.path.join(tmp_dir, "webm", raw_name + ".webm"))

if __name__ == "__main__":
	convert_batch(sys.argv[1:])
