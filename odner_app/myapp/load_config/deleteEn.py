"""
The view allows the user to delete entities from the entity model and related configurations. 
It accepts a POST request with the following parameters:

entities: a list of entities to delete from the model and configuration.
file_config: the configuration file to modify.

The view first extracts the entities to delete from the request data, and the file path of the configuration file to 
modify. It then checks if the specified configuration file is one of the base configuration files (Italian or English). If it is, it returns an error response indicating that entities cannot be deleted from the base configuration.

If the configuration file is not a base configuration file, it loads the entity model and configuration JSON file 
into dictionaries. It then iterates over the entities to delete and removes the specified entities from both 
the entity model and the configuration dictionary.

The modified configuration dictionary is then written back to the JSON file, and the modified entity model and 
configuration dictionary are saved in the corresponding Config object. The view then iterates over all the NER objects, and for each object whose JSON file is the same as the configuration file being modified, 
it removes the specified entities from the dictionary JSON file and saves the modified dictionary JSON file and entity model in the corresponding NER object.

Finally, the view iterates over all the files in the directory 'JSONDicts' and removes the specified 
entities from the dictionary if the files belong to the same configuration as the one being modified.

"""

from django.http import JsonResponse
from rest_framework import generics
from django.db import transaction
from myapp.models import NER, Config
import json
import os, re
import threading
from functools import wraps


def thread_safe(func):
    lock = threading.RLock()

    @wraps(func)
    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)

    return wrapper


@thread_safe
def JSONToDict(filename):
    """
    Convert a JSON file to a dictionary.

    :param filename: The name of the file to convert.
    :type filename: str
    :return: The dictionary resulting from the conversion.
    :rtype: dict
    """
    with open(filename) as json_file:
        data_dict = json.load(json_file)
    return data_dict


@thread_safe
def json_to_string(file_path):
    """
    Convert a JSON file to a string.

    :param file_path: The path to the JSON file to convert.
    :type file_path: str
    :return: The string resulting from the conversion.
    :rtype: str
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
        json_string = json.dumps(data)
    return json_string


@thread_safe
def DictToJSON(my_dict, filename):
    """
    Convert a dictionary to a JSON file.

    :param my_dict: The dictionary to convert to JSON.
    :type my_dict: dict
    :param filename: The name of the file to create.
    :type filename: str
    """
    with open(filename, "w") as json_file:
        json.dump(my_dict, json_file)



class DeleteEntities(generics.CreateAPIView):
    """
    A view to delete entities from the entity model and related configurations.

    :param request: the request object containing data on the entities to delete and the configuration file to modify
    :type request: HttpRequest
    :returns: a JSON response indicating the result of the deletion
    :rtype: JsonResponse
    """
    def post(self, request, *args, **kwargs):
        
        # Initialize an empty list to hold the entities to delete
        to_delete = []

        # Extract the entities to delete from the request data
        to_delete = request.data.get('entities')

        # Extract the configuration file from the request data and modify the file path to remove an encoding prefix
        file_config = request.data.get('file_config')
        file_config = re.sub("/C%3A", "C:", file_config)

        # Get the absolute path to the configuration file
        file_config = os.path.abspath(file_config)

        # Check if the configuration file is one of the base configuration files
        if (file_config[-12:] == 'base-it.json') | (file_config[-12:] == 'base-en.json'):
            # Return an error response indicating that entities cannot be deleted from the base configuration
            return JsonResponse({'cod': -1, 'res': "Non è possibile modificare entità dalla confgurazione di base"})

        # Get the Config object for the specified configuration file
        config_obj = Config.objects.filter(title=file_config).first()

        # Load the entity model from the Config object
        em_config = json.loads(config_obj.entity_model)

        # Load the configuration JSON file as a dictionary
        dict_config = JSONToDict(config_obj.json.name)

        # Iterate over the entities to delete
        for key in to_delete:
            # Check if the entity is present in the entity model
            if key in dict_config.keys():
                # Remove the entity from the entity model
                em_config.pop(key)
                # Remove the entity from the configuration dictionary
                dict_config.pop(key)

        # Write the modified configuration dictionary back to the JSON file
        DictToJSON(dict_config, config_obj.json.name)

        # Convert the modified configuration dictionary and entity model to JSON strings
        str_json = json.dumps(dict_config)
        str_em = json.dumps(em_config)

        config_to_update = Config.objects.select_for_update().filter(title=file_config).all()

        # Update the configuration object with the modified JSON strings and entity model
        with transaction.atomic():
            config_to_update.update(json_str=str_json, entity_model=str_em)

        conf = Config.objects.filter(title=file_config).first()
        conf.save

        # Get all NER objects
        queryset = NER.objects.all()

        # Iterate over the NER objects
        for ner in queryset:
            # Get the absolute path to the NER object's JSON file
            path_config = os.path.abspath(ner.jsonNER.name)

            # Check if the NER object's JSON file is the same as the configuration file being modified
            if path_config == file_config:
                # Load the NER object's dictionary JSON file as a dictionary
                json_dict = JSONToDict(ner.jsonDict.name)

                # Iterate over the entities to delete
                for key in to_delete:
                    # Check if the entity is present in the dictionary
                    if key in json_dict.keys():
                        # Remove the entity from the dictionary
                        json_dict.pop(key)

                # Write the modified dictionary back to the JSON file
                DictToJSON(json_dict, ner.jsonDict.name)

                # Convert the modified dictionary JSON file to a string

                str_dict = json_to_string(ner.jsonDict.name)

                # Update the NER object
                ner_to_update = NER.objects.select_for_update().filter(title=ner.title).all()

                with transaction.atomic():
                    ner_to_update.update(jsonDict=ner.jsonDict.name, jsondict_str=str_dict,
                                                           entity_model_current=str_em, jsonNER=file_config, jsonner_str=json_to_string(file_config))

        directory = os.path.dirname(os.path.abspath(__file__))+'\JSONDicts/'

        # Iterate over all the files in the directory 'JSONDicts'
        for root, dirs, files in os.walk(directory):
            for filename in files:
                path = os.path.abspath(os.path.join(root, filename))

                # Check if the files are of the same configuration
                if path == file_config:

                    dict = JSONToDict(path)

                    # Iterate over the entities to delete
                    for key in to_delete:
                        # Check if the entity is present in the dictionary
                        if key in dict:
                            # Remove the entity from the dictionary
                            dict.pop(key)
                    # Write the modified dictionary back to the JSON file
                    DictToJSON(dict, path)
        
        # Return JSON response to requester
        return JsonResponse({'cod': 0, 'res': "ok"})

