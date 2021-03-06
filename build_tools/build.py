import json
import os
import urllib
import zipfile
import re

from zpr.settings import BASE_DIR


class AppBuilder(object):
    JSON_NAME = 'build_conf.json'
    JSON_DIR = os.path.dirname(__file__)
    PIP_REQ = 'requirements.txt'
    PIP_REQ_LOCATION = os.path.dirname(__file__)

    def __init__(self, db_files_dir, virtenv_root, static_root):
        self.gen_conf_file_if_not_exist()
        self.conf = AppBuilder.load_conf()
        self.db_files_dir = db_files_dir
        self.virtenv = virtenv_root
        self.static_root = static_root

    @staticmethod
    def gen_conf_file():
        conf = {
            'dirs_structure': {
                'created': 0,
            },
            'db': {
                'downloaded_build_files': 0,
                'restored_ogorek_roboczy': 0,
                'built': 0,
            },
            'deploy': {
                'nginx_configurated': 0,
            },
            'instaled_pip_req': 0,
            'virtualenv': 0,
        }
        AppBuilder.save_conf(conf)

    @staticmethod
    def load_conf(name=JSON_NAME):
        with open(os.path.join(AppBuilder.JSON_DIR, name), 'rt') as data_file:
            return json.load(data_file)

    @staticmethod
    def save_conf(save_dict, name=JSON_NAME):
        with open(os.path.join(AppBuilder.JSON_DIR, name), 'wt') as outfile:
            json.dump(save_dict, outfile, sort_keys=True, indent=4, separators=(',', ': '))

    @staticmethod
    def django_debug(bool):
        set_path = os.path.join(BASE_DIR,'zpr','settings.py')
        with open(set_path, 'rt') as file:
            old_settings = file.read()
        new_settings = re.sub('(?<=DEBUG = )\w+', str(bool), old_settings, count=1)
        with open(set_path, 'wt') as file:
            file.write(new_settings)

    def _save(self):
        AppBuilder.save_conf(self.conf)

    def gen_conf_file_if_not_exist(self):
        if not os.path.exists(os.path.join(AppBuilder.JSON_DIR, AppBuilder.JSON_NAME)):
            AppBuilder.gen_conf_file()

    def create_dir_structure(self):
        dirs = [self.virtenv, self.db_files_dir, self.static_root, os.path.join(self.db_files_dir, "v3")]
        for dir in dirs:
            if not os.path.exists(dir):
                os.mkdir(dir)
        self.conf['dirs_structure']['created'] = 1
        self._save()

    def download_and_unzip_db_files(self, url):
        file_name = 'db_files.zip'
        path_file = os.path.join(self.db_files_dir, "v3", file_name)
        if self.conf['db']['downloaded_build_files'] is 0:
            print 'Pobieram pliki do budowania bazy...'
            urllib.urlretrieve(url, path_file)
            print 'Wypakowuje pliki'
            try:
                with zipfile.ZipFile(path_file, 'r') as z:
                    z.extractall(path=os.path.join(self.db_files_dir, "v3"))
                with zipfile.ZipFile(os.path.join(self.db_files_dir, "v3", "B10v2_c_corr.fsa.zip"), 'r') as z:
                    z.extractall(path=os.path.join(self.db_files_dir, "v3"))
                self.conf['db']['downloaded_build_files'] = 1
                self._save()
            finally:
                os.remove(path_file)
                os.remove(os.path.join(self.db_files_dir, "v3", "B10v2_c_corr.fsa.zip"))
            
        else:
            print self.JSON_NAME + ': Pliki bazy zostaly juz wczesniej pobrane i wypakowane'

    def create_virtualenv(self):
        if self.conf['virtualenv'] is 0:
            os.system('virtualenv --no-wheel --python=python2 {}'.format(self.virtenv))
            self.conf['virtualenv'] = 1
            self._save()
        else:
            print self.JSON_NAME + ': Virtualenv juz wczesniej utworzone'

    def install_pip_req(self):
        if self.conf['instaled_pip_req'] is 0:
            pip_path = os.path.join(self.virtenv, 'bin/pip')
            req_path = os.path.join(AppBuilder.PIP_REQ_LOCATION, AppBuilder.PIP_REQ)
            os.system('{} install -r {}'.format(pip_path, req_path))
            self.conf['instaled_pip_req'] = 1
            self._save()
        else:
            print self.JSON_NAME + ': Paczki pip juz wczesniej zainstalowane'

