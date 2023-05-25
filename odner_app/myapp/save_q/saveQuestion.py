"""
This is a Python script containing a Django view and some helper functions. The view is named "Save" and is a subclass of the Django REST Framework's `generics.CreateAPIView`. It handles HTTP POST requests and receives some data in the request body, which is used to create new configurations, add new entities to existing configurations, and update a NER (Named Entity Recognition) object with new entities and questions.

The helper functions defined in the script are:
- `DictToJSON`: it takes a dictionary and a filename, and converts the dictionary to a JSON file with the specified name.
- `JSONToDict`: it takes a filename and converts the corresponding JSON file to a dictionary.
- `json_to_string`: it takes a file path, reads a JSON file at that path, and returns its content as a string.

The view `Save` has several parameters that it receives from the request body:
- `name_entity`: the name of the entity to add or modify.
- `model`: a JSON string representing the model for the entity.
- `question`: a string representing the question for the entity.
- `answer`: a string representing the answer for the entity.
- `txt_path`: a string representing the path to the text file that the NER object relates to.
- `language`: a string representing the language of the text file.
- `new_c`: a boolean indicating whether a new configuration should be created or not.
- `c_to_change`: a string representing the name of the configuration to modify (if `new_c` is `False`).
- `name_new_config`: a string representing the name of the new configuration to create (if `new_c` is `True`).
- `file_c`: a string representing the path to the JSON file containing the configuration data.
- 'option': an integer representing the manner to create the new configuration (if `new_c` is `True`).

The view first normalizes the `txt_path` and `file_c` paths, using a regular expression. It then checks if `file_c` is present in the request. If it is not, it returns an error message. It then retrieves the NER object corresponding to the `txt_path`, if it exists.

If `new_c` is `False`, the view tries to retrieve the configuration object corresponding to `c_to_change`. If it does not exist, an error message is returned. If it exists, the view checks if the configuration is a base configuration (i.e., its name ends with "base-it.json" or "base-en.json"). If it is, an error message is returned. The view also checks if the configuration language is compatible with the text language. If it is not, an error message is returned.

If the configuration is valid, the view adds the new entity to it by updating the corresponding JSON files and database fields. It also updates the NER object with the new entity and question.

If `new_c` is `True`, the view creates a new configuration object and saves it to the database. It then updates the NER object with the new entity and question.

Finally, the view returns a JSON response containing a status code and a message.
"""

from django.http import JsonResponse
from rest_framework import generics
from myapp.models import NER, Config
import json
import os
import re
from django.db import transaction
import threading
from functools import wraps


def thread_safe(func):
    lock = threading.RLock()

    @wraps(func)
    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)

    return wrapper

# Apply the thread_safe decorator to the functions

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


class Save(generics.CreateAPIView):
    """
    This class saves new configurations, adds new entities to existing configurations and updates a NER object with new entities and questions.
    """

    lock = threading.RLock()

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests.

        :param request: HTTP request.
        :type request: HttpRequest.
        :return: HTTP response.
        :rtype: JsonResponse.
        """

        # Extract data from request body
        name_entity = request.data.get('name_entity', None)
        model = request.data.get('model', None)
        question = request.data.get('question', None)
        answer = request.data.get('answer', None)
        txt_path = request.data.get('txt_path', None)
        language = request.data.get('language', None)
        new_c = request.data.get('new_c', None)
        c_to_change = request.data.get('config_to_change', None)
        name_new_config = request.data.get('name_config_new')
        file_c = request.data.get('file_c', None)

        opt = request.data.get('option', 0)

        # Normalize file path
        txt_path = re.sub("/C%3A", "C:", txt_path)

        # Check if file_c is present in the request
        if file_c is None:
            return JsonResponse({'cod': -1, 'res': "Errore, caricamento configurazione..."})

        # Normalize file path
        file_c = re.sub("/C%3A", "C:", file_c)

        result = "ok"
        code = 0

        name_config = ""

        # Get NER object related to txt_path
        ner = NER.objects.filter(title=txt_path).first()

        # Check if it is necessary to add a new entity to an existing configuration
        if new_c is False:
            config_input = Config.objects.filter(title=c_to_change).first()

            if config_input is None:
                return JsonResponse({'cod': -1, 'res': "configurazione inesistente, scegliere una configurazione o crearne una nuova"})

            # Extract configuration name
            config_name = config_input.title[-12:]

            # Check if it is possible to add a new entity to a base configuration
            if (config_name == "base-it.json") or (config_name == "base-en.json"):
                code = -1
                result = "impossibile aggiungere la domanda a una configurazione base, crearne una nuova"
                return JsonResponse({'cod': code, 'res': result})

            # Check if configuration language is compatible with txt_path language
            if config_input.title[-7:-5] != language:
                code = -1
                result = "Lingua incompatibile, scegliere configurazione della stessa lingua del testo caricato"
                return JsonResponse({'cod': code, 'res': result})

            # Add new entity to existing configuration
            dict_1 = JSONToDict(config_input.json.name)
            if name_entity in dict_1.keys():
                return JsonResponse({'cod': -1, 'res': "nome entità già presente"})
            else:
                dict_1[name_entity] = question
                DictToJSON(dict_1, config_input.json.name)

                str_ = json_to_string(config_input.json.name)

                dict_2 = json.loads(config_input.entity_model)
                dict_2[name_entity] = model
                model_str = json.dumps(dict_2)

                queryset = Config.objects.select_for_update().filter(title=c_to_change).all()

                with transaction.atomic():

                    queryset.update(
                        json=config_input.json, json_str=str_, entity_model=model_str)

            # Update NER object with new entity and question
            if config_input.title == ner.jsonNER.name: # Current configuration
                dict = JSONToDict(ner.jsonDict.name)
                config = JSONToDict(ner.jsonNER.name)
                dict[name_entity] = []
                dict[name_entity].append(answer)
                
                config[name_entity]=question

                DictToJSON(dict, ner.jsonDict.name)
                DictToJSON(config, ner.jsonNER.name)

                em = json.loads(ner.entity_model_current)
                em[name_entity] = model

                str_dict = json_to_string(ner.jsonDict.name)
                str_config = json_to_string(ner.jsonNER.name)

                str_em = json.dumps(em)

                # Update NER obj
                queryset = NER.objects.select_for_update().filter(title=txt_path).all()

                with transaction.atomic():

                    queryset.update(jsonner_str = str_config, jsondict_str = str_dict, entity_model_current = str_em)
            
            else:
                path_dict =  ner.jsonDict.name.split('/')[:-1]

                path = ""

                name_file = txt_path.split('/')[-1]

                for part in path_dict:
                    path+=part+'/'
                
                name_config = c_to_change.split('\\')[-1]

                name_config = name_config[:-8]

                
                path_final = path+name_file[:-7]+'-'+name_config+'-'+language+'.json'

                if os.path.exists(path_final): # Json configuration file already exists

                    dict = JSONToDict(path_final)
                    dict[name_entity] = []
                    dict[name_entity].append(answer)

                    DictToJSON(dict, path_final)

                    str_config = json_to_string(c_to_change)
                    str_dict = json_to_string(path_final)

                    em = json.loads(ner.entity_model_current)

                    em[name_entity]=model

                    str_em = json.dumps(em)

                    # Update NER obj

                    queryset = NER.objects.select_for_update().filter(title=txt_path).all()

                    with transaction.atomic():
                        queryset.update(jsonDict = path_final, jsonNER = c_to_change, language=language, jsondict_str = str_dict, jsonner_str = str_config, entity_model_current = str_em)

                else:
                    
                    em = json.loads(ner.entity_model_current)

                    em[name_entity]=model

                    str_em = json.dumps(em)

                    path_base_dict = path+name_file[:-7]+'-base-'+language+'.json'

                    dict_b = {}

                    dict_b = JSONToDict(path_base_dict)

                    dict_b[name_entity] = []

                    dict_b[name_entity].append(model)

                    DictToJSON(dict_b,path_final)

                    json_dict_str = json_to_string(path_final)
                    
                    str_config = json_to_string(c_to_change)

                    # Update NER obj

                    queryset = NER.objects.select_for_update().filter(title=txt_path).all()
                    
                    with transaction.atomic():
                        queryset.update(jsonDict = path_final, jsonNER = c_to_change, language=language, jsondict_str = json_dict_str, jsonner_str = str_config, entity_model_current = str_em)
        
        # Need to create a new Config obj
        else:
            
            path_new_config = ""

            if file_c == None:
                return JsonResponse({'cod': -1, 'res': "Inserire nome nuova configurazione!"})

            file_c = file_c.split('/')[:-1]

            for part in file_c:
                path_new_config+=part+'/'

            path_new_config += name_new_config+'-'+language+'.json'

            if os.path.exists(path_new_config):
                return JsonResponse({'cod':-1, 'res': "la configurazione è già esistente"})
            else:
                if opt == 1:
                    path = path_new_config.split('/')[:-1]

                    path_base = ""

                    for part in path:
                        path_base+=part+'/'
                        

                    path_base+='/base-'+language+".json"

                    entity_model = {}

                    dict_base = JSONToDict(path_base)

                    for key in dict_base.keys():
                        entity_model[key] = "Spacy"

                    dict_base[name_entity]= []
                    dict_base[name_entity]=question

                    entity_model[name_entity] = model

                    DictToJSON(dict_base,path_new_config)

                    str_json = json_to_string(path_new_config)

                    str_model = json.dumps(entity_model)

                    path_new_config = os.path.abspath(path_new_config)

                    with transaction.atomic():
                        c = Config.objects.create(title = path_new_config, json = path_new_config, json_str= str_json, language=language, entity_model = str_model)
                        c.save()
                    
                    config = Config.objects.filter(title=path_new_config).first()
                    path_dict =  ner.jsonDict.name.split('/')[:-1]

                    path = ""

                    name_file = txt_path.split('/')[-1]

                    for part in path_dict:
                        path+=part+'/'
                    
                    path_final = path+name_file[:-7]+'-'+name_new_config+'-'+language+'.json'

                    em = json.loads(ner.entity_model_current)

                    em[name_entity] = model

                    str_em = json.dumps(em)

                    path_base_dict = path+name_file[:-7]+'-base-'+language+'.json'

                    dict_b = {}

                    dict_b = JSONToDict(path_base_dict)

                    dict_b[name_entity] = []
                    dict_b[name_entity].append(answer)

                    DictToJSON(dict_b,path_final)

                    json_dict_str = json_to_string(path_final)
                        
                    str_config = json_to_string(path_new_config)

                    # Update NER obj
                        
                    queryset = NER.objects.select_for_update().filter(title=txt_path).all()
                    
                    with transaction.atomic():
                        queryset.update(jsonDict = path_final, jsonNER = path_new_config, language=language, jsondict_str = json_dict_str, jsonner_str = str_config, entity_model_current = str_em)
                
                else:          
                    # Create a new configuration      

                    dict_entity = {}
                    
                    path_ner_dict = ner.jsonNER.name

                    entity_model = json.loads(ner.entity_model_current)

                    dict_base = {}

                    dict_base = JSONToDict(path_ner_dict)

                    for key in entity_model.keys():
                        dict_entity[key] = entity_model[key]

                    dict_base[name_entity]= []
                    dict_base[name_entity]=question

                    dict_entity[name_entity] = model

                    DictToJSON(dict_base,path_new_config)

                    str_json = json_to_string(path_new_config)

                    str_model = json.dumps(dict_entity)

                    path_new_config = os.path.abspath(path_new_config)

                    with transaction.atomic():
                        c = Config.objects.create(title = path_new_config, json = path_new_config, json_str= str_json, language=language, entity_model = str_model)
                        c.save()
                    
                    config = Config.objects.filter(title=path_new_config).first()
                    
                    path_dict =  ner.jsonDict.name.split('/')[:-1]

                    path = ""

                    name_file = txt_path.split('/')[-1]

                    for part in path_dict:
                        path+=part+'/'
                    
                    path_final = path+name_file[:-7]+'-'+name_new_config+'-'+language+'.json'

                    em = json.loads(ner.entity_model_current)

                    em[name_entity] = model

                    str_em = json.dumps(em)

                    path_base_dict = path+name_file[:-7]+'-'+name_new_config+'-'+language+'.json'

                    dict_b = {}

                    dict_b = JSONToDict(ner.jsonDict.name)

                    dict_b[name_entity] = []
                    dict_b[name_entity].append(answer)

                    DictToJSON(dict_b,path_final)

                    json_dict_str = json_to_string(path_final)
                        
                    str_config = json_to_string(path_new_config)

                    # Update NER obj
                    queryset = NER.objects.select_for_update().filter(title=txt_path).all()
                    
                    with transaction.atomic():
                        queryset.update(jsonDict = path_final, jsonNER = path_new_config, language=language, jsondict_str = json_dict_str, jsonner_str = str_config, entity_model_current = str_em)

        return JsonResponse({'cod':code, 'res': result})
            
        



            

            

             
             

        





        
        

