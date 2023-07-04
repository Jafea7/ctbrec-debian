""" Simple python client for programmatic interaction with the CTBREC server

###################################################################################
WARNING - Make a backup of your server.json file before using the CtbRec class !!!!
###################################################################################

CTBREC server functionality that is exposed includes:
* querying server state
* updating server settings
* getting/adding/modifying/deleting models
* getting/adding/modifying/deleting model-groups
* getting/deleting/post-processing recordings

Tested with ctbrec-server version 4.7.4, and Python version 3.9
"""

import json
from datetime import datetime
from enum import Enum
from typing import Union, Mapping, Optional
import uuid
import re
import hmac
import hashlib
import warnings

from urllib3.exceptions import InsecureRequestWarning
import requests


class CtbRecRequestFailed(Exception):
    """ Exception to be raised if ctbrec server returns status=='fail' """
    pass


class CtbRecInvalidModelDefinition(Exception):
    """ Exception to be raised model definition doesn't conform to recognised pattern """
    pass


class CtbRecNotFound(Exception):
    """ Exception to be raised if an attempt to match a model or group on the server fails """
    pass


class CtbRecAlreadyExists(Exception):
    """ Exception to be raised if an attempt is made to create a model-group that already exists"""
    pass


class CtbRec:
    """
    Simple Python interface to the awesome ctbrec-server
    """

    # basic regular expressions for model strings/urls
    regex = {
        'url': re.compile('https?://'),
        'site_name': re.compile(r'[A-Z]\w+:[\w-]+'),
        'domain_name': re.compile(r'https?://([\w-]+\.)*([\w-]+\.[\w-]+)/([\w-]+/)*(.*)/?$'),
        'model_type': re.compile(r'ctbrec\.sites\.[\w]+\.([\w]+)Model')
    }

    class ModelType(Enum):
        """ used for identifying model input type """
        url = 1
        site_name = 2
        model_dict = 3

    def __init__(self, server_url: str, username: str = None, password: str = None, verify: Union[bool, str] = False):
        """
        Initialise server connection

        Args:
            server_url: url of the ctbrec server, eg https://localhost:8443
            username: optional ctbrec server username  Default is None
            password: optional ctbrec server password  Default is None
            verify: Passed through to requests.Session for server ssl certificate handling. Default is False.
        """
        # ignore insecure request warnings when tls is being used
        warnings.simplefilter(action='ignore', category=InsecureRequestWarning)
        # initialise connection parameters
        self.server_url = server_url.strip("/")
        self.session = requests.Session()
        if username is not None or password is not None:
            self.session.auth = (username, password)
        self.session.verify = verify
        self.session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
        # get hmac key
        hmac_req = self.session.get(self.server_url+'/secured/hmac')
        if hmac_req.status_code == 200 and len(hmac_req.text) > 0:
            self.hmac_key = json.loads(hmac_req.text)['hmac'].encode('utf-8')
        else:
            self.hmac_key = b''
        # keep copy of initial server config
        self.initial_config = self.get_settings()
        self.initial_models = self.get_models()
        self.initial_model_groups = self.get_model_groups()

    # ----------------------------------------- model methods ---------------------------------------------------------
    def get_models(self, online: bool = False) -> Mapping[str, dict]:
        """
        Get a list of all models on the server

        Args:
            online: if True then only retrieve online models else return all models. Default is False.
        Returns:
            dict of models where key is Site:ModelName
        Raises:
            CtbRecRequestFailed
        """
        ml = self.send_request(url='/rec', data={'action': 'listOnline' if online else 'list'})['models']
        return {self.model_id(m): m for m in ml}

    def get_model_status(self) -> Mapping[str, str]:
        """
        Get status code for all models

        Returns: dict with status for each Site:Model. Status can be one of
                    ["recording", "online", "offline", "paused", "later"]
        Raises:
            CtbRecRequestFailed
        """
        m = self.get_models()
        o = self.get_models(online=True)
        r = self.get_recordings()
        result = dict.fromkeys(m.keys(), 'offline')
        result.update(dict.fromkeys(o.keys(), 'online'))
        result.update(dict.fromkeys({self.model_id(i['model']) for i in r if i['status'] == 'RECORDING'}, 'recording'))
        result.update(dict.fromkeys({k for k, v in m.items() if v['markedForLater']}, 'later'))
        result.update(dict.fromkeys({k for k, v in m.items() if v['suspended']}, 'paused'))
        return result

    def add_model(self, model: Union[str, dict], props: dict = None) -> dict:
        """
        Add a model to the server

        Args:
            model: one of [url[str], Site:Name[str], ModelDict[dict]]
            props: optional dict of one or more model definition items to update in model. These can include;
                       'priority' (integer), 'markedForLater' (True|False), 'suspended' (True|False),
                       'recordUntil' (int), 'recordUntilSubsequentAction' (string).
        Returns:
            The model dict if successfully added
        Raises:
            CtbRecInvalidModelDefinition
            CtbRecNotFound
            CtbRecRequestFailed
        """
        if props:
            props = self.parse_model_props(props)

        # determine model specification type
        mt = self.parse_model_type(model)
        if mt == self.ModelType.model_dict:
            model = self.parse_model_props(model)
            if props:
                model.update(props)
            data = {'action': 'start', 'model': model}
        elif mt == self.ModelType.site_name:
            data = {'action': 'startByName', 'model': {"type": None, "name": "", "url": model}}
        elif mt == self.ModelType.url:
            data = {'action': 'startByUrl', 'model': {"type": None, "name": "", "url": model}}
        else:
            data = {}  # should never reach here because parse_model_type will raise an exception
        # query the server
        self.send_request("/rec", data=data)
        # retrieve model back from server
        m = self.find_model(model)
        # update model dict with optional additional properties
        if props and mt != self.ModelType.model_dict:
            m = self.update_model(m, props)
        return m

    def add_models(self, models: list[Union[str, dict]], props: dict = None) -> list:
        """
        suspended=False, later=False, stop_action = 'PAUSE',

        Add a list of models to the server, catching any exceptions

        Args:
            models: a list of model definitions - one of [url[str], Site:Name[str], ModelDict[dict]]
            props: optional dict of one or more model definition items that will be applied to all models.
                        These can include;
                       'priority' (int), 'markedForLater' (bool), 'suspended' (bool),
                       'recordUntil' (int|datetime), 'recordUntilSubsequentAction' (str).
        Returns:
            A list of any models successfully added
        """
        models_added = []
        for m in models:
            try:
                models_added.append(self.add_model(m, props))
            except (CtbRecRequestFailed, CtbRecInvalidModelDefinition) as error:
                warnings.warn(f'Unable to add {m} to server: {error}')
            except CtbRecNotFound:
                warnings.warn(f'{m} added but could not be matched on server')
        return models_added

    def update_model(self, model: Union[str, dict], props: dict) -> dict:
        """ Update properties for an existing model on the server

        Args:
            model: one of [url[str], Site:Name[str], ModelDict[dict]]
            props: dict of one or more model definition items to update in model. These can include;
                       'priority' (int), 'markedForLater' (bool), 'suspended' (bool),
                       'recordUntil' (int|datetime), 'recordUntilSubsequentAction' (str).
        Returns:
            The updated model dict
        Raises:
            CtbRecInvalidModelDefinition
            CtbRecNotFound
            CtbRecRequestFailed
        """
        props = self.parse_model_props(props)
        mt = self.parse_model_type(model)
        m = model if mt == self.ModelType.model_dict else self.find_model(model)
        invalid_keys = [k for k in props if k not in m]
        if invalid_keys:
            warnings.warn(f'Invalid properties {",".join(invalid_keys)} will be ignored.')
        p = {k: v for k, v in props.items() if k in m}
        if m and p:
            m.update(p)
            self.send_request("/rec", data={"action": "start", "model": m})
            return self.find_model(m)
        warnings.warn("Failed to update model properties")
        return dict()

    def remove_model(self, model: Union[str, dict]):
        """ Delete a model from recording list on the server

        Args:
            model: one of [url[str], Site:Name[str], ModelDict[dict]]
        Raises:
            CtbRecInvalidModelDefinition
            CtbRecNotFound
            CtbRecRequestFailed
        """
        self.send_request(url='/rec', data={"action": "stop", "model":  self.find_model(model)})

    def remove_models(self, models: list[Union[str, dict]]) -> list[Union[str, dict]]:
        """ Delete a list of models from the server, catching any exceptions

        Args:
            models: list of models where elements must be one of [url[str], Site:Name[str], ModelDict[dict]]
        Returns:
            a list of any input models that failed to be removed
        """
        failed = []
        for m in models:
            try:
                self.remove_model(m)
            except (CtbRecRequestFailed, CtbRecInvalidModelDefinition, CtbRecNotFound) as error:
                failed.append(m)
                warnings.warn(f'Unable to remove {m} from server: {error}')
        return failed

    def find_model(self, model: Union[str, dict]) -> dict:
        """ get an existing model on the server by matching model input

        Args:
            model: string|dict - a ctbrec model definition
        Returns:
            model dict if model found on server
        Raises:
            CtbRecInvalidModelDefinition
            CtbRecNotFound
            CtbRecRequestFailed
        """
        models = self.get_models()
        mt = self.parse_model_type(model)
        if mt == self.ModelType.model_dict:
            match = [m for m in models.values() if m['type'] == model['type'] and m['name'] == model['name']]
        elif mt == self.ModelType.url:
            match = [m for m in models.values() if self.url_match(m['url'], model)]
        elif mt == self.ModelType.site_name and model in models:
            match = [models[model]]
        else:
            match = []
        if match:
            return match[0]
        raise CtbRecNotFound("Requested model could not be found on server.")

    # ----------------------------------------- model group methods ----------------------------------------------------
    def get_model_groups(self) -> Mapping[str, dict]:
        """
        Get a dict of all model groups currently on the server

        Returns:
          dict keyed by group-name, containing all model group dicts on the server. Model groups contain keys
          ["name", "modelUrls", "id"]
        """
        g = self.send_request(url='/rec', data={'action': 'listModelGroups'})['groups']
        return {v['name']: v for v in g}

    def delete_model_group(self, group: Union[dict, str]):
        """
        Delete a model group from the server

        Args:
            group: a group dict, or group name identifying the group to be deleted
        Raises:
            CtbRecNotFound
            CtbRecRequestFailed
        """
        if isinstance(group, str):
            g = self.find_model_group(group)
        else:
            g = group
        self.send_request(url='/rec', data={'action': 'deleteModelGroup', 'modelGroup': g})

    def save_model_group(self, group: dict):
        """
        Save a model group to the server. This will overwrite any existing information in the group.

        Args:
            group: the group dict to be saved
        Raises:
            CtbRecRequestFailed
        """
        self.send_request(url='/rec', data={'action': 'saveModelGroup', 'modelGroup': group})

    def add_models_to_group(self, group: Union[dict, str], model_list: list[Union[dict, str]]) -> dict:
        """
        Add models to an existing model group.

        Args:
            group: either a group name or a group dict, specifying an existing model group that is to be updated.
            model_list: a list of models where list items can be either au url string, or a model dict.
        Returns:
            The updated model group retrieved back from the server
        Raises:
            CtbRecNotFound
            CtbRecRequestFailed
        """
        if isinstance(group, str):
            group = self.find_model_group(group)
        ml = {m if isinstance(m, str) else m['url'] for m in model_list}
        group['modelUrls'].extend(list(ml))
        self.save_model_group(group)
        return self.get_model_groups()[group['name']]

    def remove_models_from_group(self, group: Union[dict, str], model_list: list[Union[dict, str]]):
        """
        Remove models from an existing model group.

        Args:
            group: either a group name or a group dict, specifying an existing model group that is to be updated.
            model_list: a list of models where list items can be either an url string, or a model dict.
        Returns:
            The updated model group retrieved back from the server
        Raises:
            CtbRecNotFound
            CtbRecRequestFailed
        """
        if isinstance(group, str):
            group = self.find_model_group(group)
        ml = {m if isinstance(m, str) else m['url'] for m in model_list}
        group['modelUrls'] = [m for m in group['modelUrls'] if m not in ml]
        self.save_model_group(group)
        return self.get_model_groups()[group['name']]

    def create_model_group(self, name: str, model_list: list) -> dict:
        """
        Create a new model group on the server

        Args:
            name: a string specifying name of the new group. Must be unique.
            model_list: a list of models where list items can be either an url string, or a model dict
        Returns:
            dict containing keys 'status' ('success' or 'fail')  and 'msg'
        Raises:
            CtbRecAlreadyExists
            CtbRecRequestFailed
            CtbRecNotFound
        """
        groups = self.get_model_groups()
        if name in groups:
            raise CtbRecAlreadyExists(f'Model group {name} already exists')
        ml = {m if isinstance(m, str) else m['url'] for m in model_list}  # use set to reduce to unique urls
        self.save_model_group({"name": name, 'modelUrls': list(ml), 'id': uuid.uuid4().__str__()})
        return self.get_model_groups()[name]

    def find_model_group(self, name: str) -> dict:
        """
        Retrieve an existing model group from the server by name

        Args:
          name: a string specifying name of the new group.
        Returns:
          Model-group dict
        Raises:
            CtbRecNotFound
            CtbRecRequestFailed
        """
        groups = self.get_model_groups()
        if name in groups:
            return groups[name]
        raise CtbRecNotFound(f'Model group {name} could not be found on the server')
    
    # --------------------------------------- recording methods -------------------------------------------------------
    def get_recordings(self) -> list[dict]:
        """
        Get a list of all recordings from the server

        Returns:
            list of recording dicts
        Raises:
            CtbRecRequestFailed
        """
        return self.send_request(url='/rec', data={'action': 'recordings'})['recordings']

    def delete_recording(self, recording: dict):
        """
        **Permanently** delete a recoding on server

        Raises:
            CtbRecRequestFailed
        """
        self.send_request(url='/rec', data={'action': 'delete', 'recording': recording})

    def pin_recording(self, recording: dict):
        """
        Pin a recoding on the server

        Raises:
            CtbRecRequestFailed
        """
        self.send_request(url='/rec', data={'action': 'pin', 'recording': recording})

    def unpin_recording(self, recording: dict):
        """
        Unpin a recoding on the server

        Raises:
            CtbRecRequestFailed
        """
        self.send_request(url='/rec', data={'action': 'unpin', 'recording': recording})

    def annotate_recording(self, recording: dict, note: str):
        """
        Add a note to a recoding on the server

        Raises:
            CtbRecRequestFailed
        """
        recording['note'] = note
        self.send_request(url='/rec', data={'action': 'setNote', 'recording': recording})

    def rerun_post_process(self, recording: dict):
        """
        Rerun post-processing for a recording

        Raises:
            CtbRecRequestFailed
        """
        self.send_request(url='/rec', data={'action': 'rerunPostProcessing', 'recording': recording})

    # --------------------------------------- general server methods ---------------------------------------------------
    def get_settings(self) -> list:
        """ Get current server settings

        Returns:
            list of current server settings
        Raises:
            CtbRecRequestFailed
        """
        return self.send_request(url='/config')

    def update_settings(self, settings: Union[dict, list]) -> list:
        """ Update server config settings

        Args:
            settings: either a dict of key-value pairs where keys must be valid ctbrec setting keys and values must
                   conform to expected type, or a list of ctbrec settings.
        Returns:
            list of server settings after updates have been applied
        Raises:
            CtbRecRequestFailed
        """
        if isinstance(settings, dict):
            data = {s['key']: s for s in self.get_settings()}
            for k in settings:
                if k not in data.keys():
                    warnings.warn(f'{k} is not a valid settings key and will be ignored')
                data[k]['value'] = settings[k]
            data = list(data.values())
        else:
            data = settings
        self.send_request(url='/config', data=data)
        return self.get_settings()

    def get_space(self) -> dict:
        """ Get drive space statistics from server

        Returns:
            dict of drive space statistics
        Raises:
            CtbRecRequestFailed
        """
        return self.send_request(url='/rec', data={'action': 'space'})

    def get_summary(self) -> dict:
        """ Get summary of server activity

        Returns:
            dict of drive space statistics
        Raises:
            CtbRecRequestFailed
        """
        models = self.get_models()
        paused = len([m for m in models.values() if m['suspended']])
        later = len([m for m in models.values() if m['markedForLater']])
        online = len(self.get_models(online=True))
        recordings = self.get_recordings()
        recording = len([r for r in recordings if r['status'] == 'RECORDING'])
        post_process = len([r for r in recordings if r['status'] == 'POST_PROCESSING'])
        space = self.get_space()
        return {"total_models": len(models), "models_recording": recording, "models_online": online,
                "models_paused": paused, "models_marked_later": later, "total_recordings": len(recordings),
                "post_processing": post_process,
                "space_used": f"{round((space['spaceTotal']-space['spaceFree'])/1e9,3)} GB",
                "space_free": f"{round(space['spaceFree']/1e9,3)} GB"}

    def pause_recording(self):
        """ Suspend all recoding on the server

        Raises:
            CtbRecRequestFailed
        """
        self.send_request(url='/rec', data={'action': 'pauseRecorder'})

    def resume_recording(self):
        """ Resume all recoding on the server

        Raises:
            CtbRecRequestFailed
        """
        self.send_request(url='/rec', data={'action': 'resumeRecorder'})


    # ------------------------------------------- internal methods -----------------------------------------------------
    def type_to_site(self, model_type: str) -> str:
        """
        Get ctbrec site code from ctbrec site class name

        Args:
            model_type: str containing ctbrec model type code
        """
        return re.findall(self.regex['model_type'], model_type)[0]

    def parse_model_props(self, props: dict) -> dict:
        """
        Process model properties. At the moment this only adjusts 'recordUntil' if it is specified as a datetime or
        in hours.

        Args:
            props: dict containing model properties
        Returns:
            model dict after converting recordUntil to a timestamp
        """
        p = props
        if p and 'recordUntil' in p:
            record_until = p['recordUntil']
            if isinstance(record_until, datetime):
                p['recordUntil'] = round(record_until.timestamp()*1000)
            elif isinstance(record_until, int) and record_until < 10000:   # assume it is specified in hours
                p['recordUntil'] = round(datetime.now().timestamp()*1000 + record_until*3600000)
        return p

    def model_id(self, model: dict) -> str:
        """
        Get model id from model dict. Id is Site:ModelName

        Args:
            model: ctbrec model dict
        """
        return re.findall(self.regex['model_type'], model['type'])[0] + ':' + model['name']

    def url_match(self, url1: str, url2: str) -> bool:
        """ Check if two urls match, either exact match or by top level domain and name

        This makes the assumption that model name is the last string in the url, which seems to be the case at the
        moment, may not always be true in the future
        """
        u1 = url1.strip().rstrip('/')
        u2 = url2.strip().rstrip('/')
        if u1 == u2:
            return True
        u1g = re.findall(self.regex['domain_name'], u1)[0]
        u2g = re.findall(self.regex['domain_name'], u2)[0]
        return u1g[1] == u2g[1] and u1g[3] == u2g[3]

    def parse_model_type(self, model: Union[str, dict]) -> ModelType:
        """ Determine model request type from model input """
        if isinstance(model, dict) and all(k in model for k in ['type', 'name', 'url']):
            return self.ModelType.model_dict
        elif isinstance(model, str) and re.match(self.regex['url'], model):
            return self.ModelType.url
        elif isinstance(model, str) and re.match(self.regex['site_name'], model):
            return self.ModelType.site_name
        raise CtbRecInvalidModelDefinition("Model must be one of [url[str], Site:Name[str], ModelDict[dict]]")

    def send_request(self, url: str, data: Optional[Union[dict, list]] = None) -> Union[dict, list]:
        """ Send a request to the ctbrec server

        Args:
            url: string - relative url for the request, eg. '/rec'
            data: dict - payload to send to server. If None then GET will be used rather than POST
        Return:
            server result data structure
        Raises:
            CtbRecRequestFailed
        """
        data_str = '' if data is None else json.dumps(data)
        data_hmac = hmac.new(self.hmac_key, data_str.encode('utf-8'), hashlib.sha256).hexdigest()
        self.session.headers.update({'CTBREC-HMAC': data_hmac})
        if data is None:
            result = self.session.get(self.server_url + url)
        else:
            result = self.session.post(self.server_url+url, data=data_str)
        if result.status_code == 200:
            result_json = json.loads(result.text)
            if isinstance(result_json, dict) and result_json['status'] != "success":
                raise CtbRecRequestFailed(f"Request failed: {result_json['msg']}")
            else:
                return result_json
        else:
            raise CtbRecRequestFailed(f'HTTP error: {result.status_code} : {result.reason} : {result.text}')
