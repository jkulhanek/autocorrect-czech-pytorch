import requests
import io
import zipfile
from collections import namedtuple
import tempfile
import os

DownloaderContext = namedtuple('DownloaderContext', ['base_url', 'resources_path'])

class Downloader:
    def __init__(self):
        self.base_url = 'https://deep-rl.herokuapp.com/resources/'
        self.resources = dict()
        self._base_path = None

    @property
    def base_path(self):
        if self._base_path is None:
            self._base_path = os.path.expanduser('~/.autocorrect-czech')
        return self._base_path

    @property
    def resources_path(self):
        return os.path.join(self.base_path, 'resources')

    def create_context(self):
        return DownloaderContext(self.base_url, self.resources_path)

    def add_resource(self, name, fn):
        self.resources[name] = fn

    def get(self, name):
        return self.resources[name](self.create_context())

downloader = Downloader()

def download_resource(name, context, url = None):
    resource_path = os.path.join(context.resources_path, name)
    if os.path.exists(resource_path):
        return resource_path

    if url is None:
        url = context.base_url + '%s.zip' % name
    try:
        print('Downloading resource %s.' % name)  
        response = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(resource_path)

        print('Resource %s downloaded.' %name)
        return resource_path

    except Exception as e:
        if os.path.exists(resource_path):
            os.remove(resource_path)
        raise e

def download_resource_task(name, url = None):
    def thunk(context):
        return download_resource(name, context, url)
    return thunk

def download_phword_task():
    url = 'http://www.ujc.cas.cz/phword/czphtextcorp_29-06-16.zip'
    def thunk(context):
        resource = download_resource('phword', context, url = url)
        resource = extract_phword(resource)
        resource = extract_embedding(resource)
        return resource
    return thunk

def add_resources(downloader):
    downloader.add_resource('phword', download_phword_task())

add_resources(downloader)

def resource(name):
    return downloader.get(name)



def extract_phword(path):
    import os
    from xml.dom.minidom import parse

    rpath = os.path.join(path, 'dataset.txt')
    if os.path.isfile(rpath):
        return rpath

    with open(rpath, 'w+', encoding = 'utf-8') as fout:
        for f in os.listdir(path):
            if not f.endswith('.xml'):
                continue
            try:
                obj = parse(os.path.join(path, f))
            except Exception as e:
                print('ERROR: invalid file %s' % os.path.join(path, f))
                raise e

            for x in obj.getElementsByTagName('line'):
                fout.write(x.firstChild.data + '\n')
        fout.flush()
    return rpath

def extract_embedding(path):
    rpath = os.path.join(os.path.dirname(path), 'embedding.txt')
    if os.path.isfile(rpath):
        with open(rpath, 'r') as f:
            characters = f.read().strip('\n')
        return (path, list(characters))

    characters = set()

    with open(path, 'r', encoding = 'utf-8') as f:
        for line in f.readlines():
            line = line.strip('\n')
            for char in line:
                characters.add(char)

    characters = list(characters)
    characters.sort(key = lambda x: ord(x))
    with open(rpath, 'w', encoding = 'utf-8') as f:
        f.write(u''.join(characters))
        f.flush()

    return (path, characters)


