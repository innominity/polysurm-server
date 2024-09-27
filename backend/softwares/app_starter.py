import os
from django.conf import settings
from .models import SoftwareApp, SoftwareAppTask, SoftwareAppTaskFileConfig
import shutil
import pathlib
import json
import importlib.util
import sys


class RemoteAppSoftware:
    "Класс программное обеспечение на сервере"

    ROOT_APP_TASKS_PATH = os.path.join(settings.MEDIA_ROOT, "tasks")
    MODULE_NAME = "remote_software_app"

    def __init__(self, software_app_guid, software_app_task_guid=None) -> None:
        """Инициализация програмного обеспечения или ее задачи в зависимости от переданного параметра

        Args:
            software_app_guid (_type_): _description_
            software_app_task_guid (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
        """
        if software_app_guid is None and software_app_task_guid is None:
            raise Exception(
                "Должен быть передан либо GUID приложения либо GUID задачи выполнения приложения"
            )
        
        self.__software_app_guid = str(software_app_guid)
        self.__software_app_task_guid = software_app_task_guid
        self.__guid_config_files = None
        
        if software_app_task_guid is not None:
            self.__guid_config_files = self.load_config_files()

    def create_software_task(self):
        """Создание задачи запуска ПО

        Args:
            software_app_guid (str): GUID задачи из базы данных модель SoftwareApp

        Returns:
            str: GUID задачи выполнения ПО (модель SoftwareAppTask)
        """
        software_app = SoftwareApp.objects.get(guid=self.__software_app_guid)
        software_app_task = SoftwareAppTask(
            software_app=software_app, status=SoftwareAppTask.TaskStatus.NOT_STARTED
        )
        software_app_task.save()
        self.__software_app_task_guid = str(software_app_task.guid)
        return str(self.__software_app_task_guid)

    def attach_config_files(self, guid_config_files):
        """Метод закрепления файлов конфигурации за экземпляром выполнения ПО

        Args:
            guid_config_files (list[str], optional): Список GUID файлов конфигурации из бд модель SoftwareAppTaskFileConfig. Defaults to None.
        """
        print(self.__software_app_task_guid)
        app_task = SoftwareAppTask.objects.get(guid=self.__software_app_task_guid)
        app_task_dir = self.get_app_task_folder(self.__software_app_task_guid)

        for guid_config_file in guid_config_files:

            config_file = SoftwareAppTaskFileConfig.objects.get(guid=guid_config_file)
            config_file_path = config_file.config_file.path
            config_filename = config_file.config_filename
            if config_filename == "":
                raise Exception("Ошибка чтения имения файла конфигурации!")
            # Закрепляем конфиг файл за задачей
            config_file.software_app_task = app_task
            config_file.save()
            # копируем файл конфигурации в папку приложения
            app_config_file_path = os.path.join(app_task_dir, config_filename)
            shutil.copyfile(config_file_path, app_config_file_path)

    def load_config_files(self):
        return None

    def create_app_subfolder(self):
        """Создания директории для выполнения ПО"""
        if self.__software_app_task_guid:
            software_app = SoftwareApp.objects.get(guid=self.__software_app_guid)
            folder_app_run = self.get_app_task_folder(self.__software_app_task_guid)
            current_dir = os.path.join(settings.BASE_DIR, 'softwares')
            folder_app = os.path.join(current_dir, 'apps', software_app.slug)
            shutil.copytree(folder_app, folder_app_run)
        else:
            raise ValueError('Для создания папки задачи необходимо создать задачу методом "create_software_task"')
        
    def run(self, config_params=None, guid_config_files=None):
        """Метод запуска задачи выполнения ПО с переданными параметрами

        Args:
            config_params (dict, optional): _description_. Defaults to None.
            guid_config_files (dict, optional): _description_. Defaults to None.

        Returns:
            tuple: Результат выполнения задачи и статус
        """
        if self.__software_app_task_guid is not None:
            raise Exception('Задача уже существует')
        
        self.create_software_task()
        software_task = SoftwareAppTask.objects.get(guid=self.__software_app_task_guid)
        software_task.status = SoftwareAppTask.TaskStatus.PROCESSING
        software_task.save()
        self.create_app_subfolder()
        if guid_config_files is not None:
            self.attach_config_files(guid_config_files)

        app_dir = self.get_app_task_folder(self.__software_app_task_guid)
        app_module_path = os.path.join(app_dir, "app.py")
        module_name = "remote_software_app"

        spec = importlib.util.spec_from_file_location(module_name, app_module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        remote_software = module.RemoteAppSoftware(app_dir)
        if config_params is not None:
            remote_software.config = dict(config_params)

        results = remote_software.run()
        software_task.status = SoftwareAppTask.TaskStatus.SUCCESS
        software_task.save()
        return {'status':'success', 'results': results}
        
    @classmethod
    def get_app_task_folder(cls, app_task_guid: str) -> str:
        """Метод получения пути до директории выполнения ПО

        Args:
            app_task_guid (str): GUID задачи из базы данных модель SoftwareAppTask

        Returns:
            str: путь расположения ПО и файлов конфигурации
        """
        if not app_task_guid:
            raise Exception("Не передан GUID приложения!")
        software_app_task = SoftwareAppTask.objects.filter(guid=app_task_guid)
        if len(software_app_task) == 0:
            raise Exception("Задач выполнения программного обеспечения не найдена!")
        return os.path.join(cls.ROOT_APP_TASKS_PATH, app_task_guid)
    
    @classmethod
    def get_config_params(cls, app_guid: str) -> list:
        """Метод получения параметров ПО

        Args:
            app_task_guid (str): GUID задачи из базы данных модель SoftwareAppTask

        Returns:
            dict: словарь входных параметров ПО
        """
        software_app = SoftwareApp.objects.get(guid=app_guid)
        config_params = {}
        params_path = os.path.join(settings.BASE_DIR, 'softwares', 'apps', software_app.slug, 'params.json')
        if os.path.exists(params_path):
            with open(params_path, encoding='utf-8') as f:
                config_params = json.load(f)
        return config_params


    