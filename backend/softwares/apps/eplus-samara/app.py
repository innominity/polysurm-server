import os
import shutil
import subprocess
import uuid
from typing import Tuple
from django.conf import settings
import json
from itertools import islice
import numpy as np
from string import Template
import hashlib


def get_hash(config_dict: dict) -> str:
    data = json.dumps(config_dict)
    return hashlib.sha256(data.encode()).hexdigest()


def json_save(data, file, ensure_ascii=False, indent=4, sort_keys=True):
    with open(file, 'w', encoding='utf-8') as fp:
        json.dump(
            data,
            fp,
            ensure_ascii=ensure_ascii,
            indent=indent,
            sort_keys=sort_keys,
        )


def json_load(file) -> dict:
    with open(file, 'r', encoding='utf-8') as fp:
        return json.load(fp)


class RemoteAppSoftware:
    """Базовый класс для обертки над функциональностью программы"""

    def __init__(self, app_dir_path):
        self.app_dir_path = app_dir_path
        self.config = {}
        self.cache_dir = 'eplus-samara'

        self.default_config = {
            'max_DBT_W': -17.3,
            'BP_W': 99063.0,
            'wind_speed_W': 4.9,
            'wind_dir_W': 270,
            'sky_clearness_W': 0.0,
            'max_DBT_S': 31.5,
            'BP_S': 99063.0,
            'wind_speed_S': 5.3,
            'wind_dir_S': 230,
            'sky_clearness_S': 1.0,
        }

        self.__template_file = "template.idf"
        self.__input_file = "input.idf"
        self.__weahter_file = "weather.epw"

        self._output_file = 'eplustbl.csv'
        self._error_file = 'eplusout.err'
        self._end_file = 'eplusout.end'

    @property
    def app_dir_path(self):
        return self.__app_dir_path

    @app_dir_path.setter
    def app_dir_path(self, app_dir_path):
        self.__app_dir_path = app_dir_path

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, config: dict):
        self.__config = config

    def __run_local(self, config: dict):
        print('params', config)
        self.__update_config(config)
        self.__eplusrun().wait()
        results = self._parse_output_file()
        return results

    def run(self): 
        cache_dir_path = os.path.join(settings.MEDIA_ROOT, 'cache', self.cache_dir)
        if not os.path.exists(cache_dir_path):
            os.makedirs(cache_dir_path)

        results = {} 
        for i in self.config:
            config = self.config[i]
            hash_str = get_hash(config)
            hash_str_file = os.path.join(cache_dir_path, hash_str+'.json')

            result = {}
            if os.path.exists(hash_str_file):
                # есть кеш то его возвращаем
                result = json_load(hash_str_file)

            if not result:
                nse = self.__run_local(config)

                if nse is None:
                    continue

                result = {'net_site_energy': nse}
                json_save(result, hash_str_file)

            results[i] = result #{'net_site_energy': nse}

        self.dispose()
        return results     

    def __update_config(self, params) -> Tuple[str, str]:
        with open(os.path.join(self.app_dir_path, self.__template_file), 'r') as file:
            template_text = file.read()

        self._template = Template(template_text)

        filled_template_text = self._template.substitute(params)

        input_path = os.path.join(self.app_dir_path, self.__input_file)
        with open(input_path, 'w') as file:
            file.write(filled_template_text)

        return input_path
    

    def _parse_output_file(self):
        num_line = 16
        num_column = 3
        output_path = os.path.join(self.app_dir_path, self._output_file)

        with open(output_path) as f:
            line = next(islice(f, num_line - 1, num_line))

        return float(line.split(',')[num_column + 1])

    def validate_config_dict(self):
        pass

    def __eplusrun(self) -> subprocess.Popen:
        args = [
            "energyplus",
            "-w",
            os.path.join(self.app_dir_path, self.__weahter_file),
            os.path.join(self.app_dir_path, self.__input_file),
        ]
        return subprocess.Popen(args, cwd=self.app_dir_path)

    def dispose(self):
        folder = self.app_dir_path
        try:
            shutil.rmtree(folder)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (folder, e))
