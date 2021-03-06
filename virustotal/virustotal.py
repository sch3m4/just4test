import hashlib
from fame.core.module import ProcessingModule
from fame.common.exceptions import ModuleInitializationError
from fame.common.utils import tempdir

try:
    import requests
    HAVE_REQUESTS = True
except:
    HAVE_REQUESTS = False

class VirusTotal(ProcessingModule):
    name = "virustotal_check"
    description = "Check file hash with virustotal"

    config = [
        {
            'name': 'API',
            'type': 'str',
            'description': 'API Key'
        },
        {
            'name': 'URL',
            'type': 'str',
            'description': 'API URL',
            'default': 'https://www.virustotal.com/vtapi/v2/file/report'
        }
    ]


    def initialize(self):
        if not HAVE_REQUESTS:
            raise ModuleInitializationError(self, "Missing dependency: requests")


    def each(self, target):
        self.results = {}
        alg = hashlib.sha256()
        with open(target,'rb') as f:
            buf = f.read(1024)
            while len(buf) > 0:
                alg.update(buf)
                buf = f.read(1024)
        fhash = alg.hexdigest()

        params = {'resource': fhash, 'apikey': self.API}
        try:
            data = requests.get(self.URL,params=params).json()
        except:
            return False

        if data['response_code'] == 0:
            return False

        if not 'positives' in list(data.keys()) or not data['positives']:
            return False

        self.results = {'positives': data['positives'],'link':data['permalink']}

        return True
