import os
import subprocess
import uuid
from typing import Tuple
from django.conf import settings
import json
import numpy as np


class RemoteAppSoftware:
    """Базовый класс для обертки над функциональностью программы"""

    def __init__(self, app_dir_path):
        self.app_dir_path = app_dir_path
        self.config = {}
        self.default_config = {
            "xp": 0,
            "yp": 0,
            "xlen": 20750,
            "ylen": 20750,
            "mx": 30,
            "my": 30,
            "velocity": 5,
            "direction": 315,
        }

        self.__template_file = "template.swn"
        self.__input_file = "input.swn"
        self.__output__file = ""

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
        params = self.default_config.copy()
        params.update(config)
        self.__output_file = self.__update_config(**params)
        self.__swanrun().wait()
        output_path = os.path.join(self.app_dir_path, self.__output_file)
        hs = None
        if os.path.exists(output_path):
            hs = np.fromfile(output_path, sep=" ")
            mx, my = params["mx"], params["my"]
            hs = hs.reshape(my + 1, mx + 1)

        self.dispose()
        if hs is not None:
            return hs
        else:
            return []

    def run(self):
        points = {
            'hs_bay': (28, 26),
            'hs_sea': (11, 11),
        }
        result = {} 
        print(self.config)
        for i in self.config:
            config = self.config[i]

            out = {} #cache.get(hash, {})

            if not out:
                hs = self.__run_local(config)

                if hs is None:
                    continue

                for point, coord in points.items():
                    out[point] = hs[coord]

            result[i] = out
        return result

    def __update_config(self, **params) -> Tuple[str, str]:
        template_path = os.path.join(self.app_dir_path, self.__template_file)
        with open(template_path, "r") as file:
            template_text = file.read()

        output_file = params.pop("fname", str(uuid.uuid4()))
        filled_template_text = template_text.format(fname=output_file, **params)

        input_path = os.path.join(self.app_dir_path, self.__input_file)
        with open(input_path, "w") as file:
            file.write(filled_template_text)

        return output_file
    

    def validate_config_dict(self):
        pass

    def __swanrun(self) -> subprocess.Popen:
        args = [
            "sh",
            os.path.join(self.app_dir_path, "swanrun"),
            "-input",
            self.__input_file[:-4],
        ]
        return subprocess.Popen(args, cwd=self.app_dir_path)

    def dispose(self):
        files = [
            f"{self.__input_file[:-4]}.prt",
            self.__input_file,
            self.__output_file,
            "norm_end",
            "swaninit",
        ]

        for file in files:
            path = os.path.join(self.app_dir_path, file)
            if os.path.exists(path):
                os.remove(path)
