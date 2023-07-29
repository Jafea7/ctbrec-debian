#!/bin/python3
 
from ctbrec import CtbRec
import os
import time

srv_url=os.environ.get('SRVURL')
srv_usr=os.environ.get('SRVUSR')
srv_pss=os.environ.get('SRVPSS')
recover=int(os.environ.get('RECOVER'))

# Create CTBRec Python client instance
ctb = CtbRec(server_url=srv_url, username=srv_usr, password=srv_pss)

# Get disk space
space=ctb.get_space()
minspace=(space['spaceFree'] + recover)
print('reclaim.py\nFree:     ' + space['spaceFree'] + '\nRequired: ' + minspace)

# Get recordings
recordings = ctb.get_recordings()
if recordings:
  index = 0
  for record in recordings:  
    if not record['pinned'] and (record['status'] == 'FINISHED'):
      if ((ctb.get_space())['spaceFree'] < minspace):
        ctb.delete_recording(recordings[index])
        print(record['metaDataFile'] + " - Deleted")
        time.sleep(2)
    index += 1
