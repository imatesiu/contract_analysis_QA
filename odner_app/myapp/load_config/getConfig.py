"""
This is a Django view that retrieves or creates Config objects based on the specified language. It first retrieves the 
language from the HTTP request data and initializes an empty list to store the paths of the Config objects. 
It then defines the directory where the JSON config files are stored and loads the base English and Italian entity models from JSON files, 
updating them with the "Spacy" model type. 

Next, the view loops through all files in the directory and retrieves the paths of the Config objects that match the specified language. 
If the Config object does not already exist in the database, it creates it with the appropriate entity model. 
Finally, it returns a JSON response containing the paths of the Config objects.

The `DictToJSON` function is used to convert a dictionary to a JSON file, `JSONToDict` 
function is used to convert a JSON file to a dictionary, and `json_to_string` function is used to convert a JSON file to a string. 
These functions are used within the `post` method to load and manipulate the entity models. 

The `GetConfig` class is a generic `CreateAPIView` that handles POST requests. It receives a request 
containing data about the language and uses this data to retrieve or create Config objects in the database. 
It then returns a JSON response containing the paths of the Config objects.

"""

from django.http import JsonResponse
from rest_framework import generics
from myapp.models import Config
import os
import json
from django.db import transaction
import threading

from functools import wraps
from transformers import pipeline

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
  
class GetConfig(generics.CreateAPIView):
    """
    View to retrieve and create Config objects based on request data.
    """

    def post(self, request, *args, **kwargs):
        """
        Retrieves or creates Config objects based on the specified language.
        
        :param request: The HTTP request sent to the view.
        :type request: django.http.HttpRequest
        :param args: Additional arguments passed to the view.
        :param kwargs: Additional keyword arguments passed to the view.
        :return: A JSON response containing a list of paths to the retrieved or created Config objects.
        :rtype: django.http.JsonResponse
        """

        # Retrieve the specified language from the request data
        l = request.data.get('language', None)

        # Initialize an empty list to store the paths of the Config objects
        entities = []

        # Define the directory where the JSON config files are stored
        directory = os.path.dirname(os.path.abspath(__file__)) + '\json_configs/'

        # Load the base English entity model from a JSON file and update it with the "Spacy" model type
        entity_model_en = JSONToDict(directory + 'base-en.json')
        for key in entity_model_en.keys():
            entity_model_en[key] = "Spacy"
        json_string_en = json.dumps(entity_model_en)

        

        # Load the base Italian entity model from a JSON file and update it with the "Spacy" model type
        entity_model_it = JSONToDict(directory + 'base-it.json')
        for key in entity_model_it.keys():
            entity_model_it[key] = "Spacy"
        json_string_it = json.dumps(entity_model_it)
        

        # Loop through all files in the directory and retrieve the paths of the Config objects that match the specified language
        for root, dirs, files in os.walk(directory):
            for filename in files:
                path = os.path.abspath(os.path.join(root, filename))
                language = path[-7:-5]
                if l == language:
                    entities.append(path)

                # If the Config object does not already exist in the database, create it with the appropriate entity model
                if Config.objects.filter(title=path).first() is None:
                    
                    
                    with transaction.atomic():
                        if language == 'it':
                            c = Config.objects.create(title=path, json=path, json_str=json_to_string(path),
                                              language=language, entity_model=json_string_it)
                        
                        
                        
                        else:
                            c = Config.objects.create(title=path, json=path, json_str=json_to_string(path),
                                              language=language, entity_model=json_string_en)
                        c.save()

        # Return a JSON response containing the paths of the Config objects
        return JsonResponse({'configs': entities})