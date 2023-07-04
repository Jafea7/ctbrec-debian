#!/bin/python3
import os
from ctbrec import CtbRec

srv_url=os.environ.get('SRVURL')
srv_usr=os.environ.get('SRVUSR')
srv_pss=os.environ.get('SRVPSS')
# create CtbRec python client instance
ctb = CtbRec(server_url=srv_url, username=srv_usr, password=srv_pss)

# get recordings
recordings = ctb.get_recordings()
if recordings:
  print("Number of recordings:", len(recordings))
  index = 0
  for record in recordings:
    if not os.path.exists(record['absoluteFile']):
      print(record['absoluteFile'] + " - " + record['status'])
      if record['status'] == 'FINISHED':
        ctb.delete_recording(recordings[index])
        print(record['metaDataFile'] + " - Deleted")
    index += 1
