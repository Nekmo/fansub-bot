from logging import getLogger
import os
import subprocess
import tempfile
import shutil

TEMP_DIR = tempfile.tempdir if tempfile.tempdir else '/tmp'


__author__ = 'nekmo'

logger = getLogger('utils.torrent')


# def create_torrent_pack(local_files, torrent_data):
#     logger.log("create torrent pack")
#     success, files = self.search_file("mkv", self.directory)
#     if not success:
#         return
#     announce_url_list = torrent_data.get("announce_url")
#     announce_url = " -a".join(announce_url_list)
#     local_file = self.get_name()
#     envoy.run("rm -rf  /tmp/pack" )
#     directory_name = self.name.replace(".torrent", "")
#     envoy.run("mkdir -p /tmp/pack/%s" % directory_name)
#     envoy.run("cp  %s /tmp/pack/%s  -rf" % ( " ".join(local_files) , directory_name ))
#     out_file = pipes.quote(os.path.join(self.dir, local_file))
#     cmd = "mktorrent %s -a %s -n %s  -o %s" % ("/tmp/pack/%s" % directory_name,announce_url,local_file.replace(".torrent",""),out_file)
#     logger.log("creando torrent torrent")
#     logger.log(cmd)
#     envoy.run(cmd)
#     s, torrent_file = self.search_file("torrent", self.directory)
#     #envoy.run("rm /tmp/pack -rf ")
#     if s:
#         return torrent_file


def create_torrent(local_files, output, announce_urls, directory_name=None):
    if len(local_files) > 1:
        # return create_torrent_pack(local_files, torrent_data)
        if directory_name is None:
            source = tempfile.mkdtemp(prefix='tmp-torrent-dir', dir=TEMP_DIR)
        else:
            source = os.path.join(TEMP_DIR, directory_name)
            os.makedirs(source)
        for local_file in local_files:
            os.symlink(local_file, os.path.join(source, os.path.split(local_file)[1]))
    else:
        local_files = list(local_files)
        source = local_files.pop()
    logger.info("creando torrent")
    announce_urls = ",".join(announce_urls)
    if os.path.exists(output):
        os.remove(output)
    subprocess.call([
        'mktorrent', source, '-a', announce_urls, '-o', output
    ])
    if len(local_files) > 1:
        shutil.rmtree(source)