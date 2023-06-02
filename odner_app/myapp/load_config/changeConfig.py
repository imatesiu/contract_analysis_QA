"""
The utility functions in this script are:
    - ner(txt_to_ner, language): performs Named Entity Recognition (NER) on text using Spacy and returns the named entities as a dictionary.
    - DictToJSON: a function that takes a dictionary and a filename, and writes the contents of the dictionary to a JSON file with the given filename.
    - JSONToDict: a function that takes a filename and returns a dictionary containing the contents of the JSON file with the given filename.
    - json_to_string: a function that takes a file path and returns a string representation of the JSON data in the file.

configChange: a class-based view that handles POST requests for configuration changes.

    The configChange class-based view contains a post method that takes a POST request, retrieves the necessary data from the request, and updates the relevant models in the database.

    The configChange view first retrieves the txt_file_path, context, name_config, and language parameters from the request. 
    It then retrieves the Config and NER models associated with the given name_config and txt_file_path, respectively.

    If the language associated with the Config and NER models does not match, the view returns a JSON response indicating that the language is incompatible. 
    If the JSON file associated with the Config model is already the current JSON file associated with the NER model, the view returns a JSON response indicating that the configuration is already current.

    Otherwise, the view updates the JSON file associated with the NER model. If the file already exists, the view adds any missing entities to the JSON file by using a question-answering model 
    to extract the relevant information from the context. If the file does not exist, the view creates a new JSON file based on a base dictionary and updates the NER object with the new JSON file.

"""

from django.http import JsonResponse
from rest_framework import generics
from myapp.models import NER, Config
import json
import os
from transformers import pipeline
import re
from django.db import transaction
import spacy
import threading
from functools import wraps
import spacy_transformers



def ner(txt_to_ner, language):
    """
    Performs Named Entity Recognition (NER) on text.

    :param
        txt_to_ner (str): The text to perform NER on.
        language (str): The language of the text to be processed. Supported languages are 'en' for English and 'it' for Italian.

    :return
        dict: A dictionary where keys are named entity labels and values are lists of named entities for each label.
    """
    if language == 'it':
        nlp = spacy.load("it_core_news_lg")
    else:
        nlp = spacy.load("en_core_web_trf")

    # perform NER on text
    doc = nlp(txt_to_ner)

    # create dictionary to store named entities by label
    tmp = {label: [] for label in nlp.get_pipe('ner').labels}

    # loop through named entities and store them in the dictionary by label
    for ent in doc.ents:
        tmp[ent.label_].append(ent.text)

    return tmp


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



class configChange(generics.CreateAPIView):
    """
    Class-based view for handling configuration changes.

    """
    lock = threading.RLock()


    def post(self, request, *args, **kwargs):
        """
        Handle a POST request.

        :param request: The request to handle.
        :type request: HttpRequest
        :return: A JSON response indicating the success or failure of the request.
        :rtype: JsonResponse
        """

        # Get text file, text to perform qa and extract the NER, filename of the configuration and the language
        txt_file_path = request.data.get('txt', None)

        txt_file_path = re.sub("/C%3A", "C:", txt_file_path)

        context = request.data.get('context', None)

        name_config = request.data.get('config_name', None)

        # absolute path of the configuration
        name_config = os.path.abspath(name_config)

        language = request.data.get('language',None)

        if name_config == None:
            return JsonResponse({'cod': -1, 'res': "selezionare una configurazione"})

        # Retrieve Config object
        config_obj = Config.objects.filter(title=name_config).first()

        # Retrieve NER object
        ner_obj = NER.objects.filter(title=txt_file_path).first()


        if config_obj.language != ner_obj.language:
            return JsonResponse({'cod': -1, 'res': "lingua incompatibile"})

        # Build path name (path_final) of the JSON file containing the specified NER
        path_dict =  ner_obj.jsonDict.name.split('/')[:-1]

        path = ""

        name_file = txt_file_path.split('/')[-1]

        for part in path_dict:
            path+=part+'/'
                
        name_config = name_config.split('\\')[-1]

        name_config = name_config[:-8]

        path_final = path+name_file[:-7]+'-'+name_config+'-'+language+'.json'
       
        em = json.loads(config_obj.entity_model)

        dict_question = JSONToDict(config_obj.json.name)

        # If the file JSON associated to the NER exists
        if os.path.exists(path_final):  

            str_dict = json_to_string(path_final)

            str_em = json.dumps(em)

            ner_to_update = NER.objects.select_for_update().filter(title=txt_file_path).all()

            with transaction.atomic():
                # Update NER object
                ner_to_update.update(jsonDict=path_final, jsondict_str = str_dict, jsonNER = config_obj.json, jsonner_str = config_obj.json_str, entity_model_current = str_em)
            
        else: 
            
            path_base_dict = path+name_file[:-7]+'-base-'+language+'.json'

            dict_b = {}

            # Retrieve config-base dictionary
            dict_b = JSONToDict(path_base_dict)

            for key in em.keys():
                if em[key] != 'Spacy':
                    if key not in dict_b.keys():

                        question = dict_question[key] 


                        with self.lock:

                            qa = pipeline("question-answering", model=em[key])

                            result = qa(question=question, context=context)

                        answer = result['answer']

                        dict_b[key] = []

                        dict_b[key].append(answer)
            
            # Write the modified dictionary back to the JSON file
            DictToJSON(dict_b, path_final)

            str_dict = json_to_string(path_final)

            str_em = json.dumps(em)

            # Update NER object with new JSON dictionary
            ner_to_update = NER.objects.select_for_update().filter(title=txt_file_path).all()
            
            with transaction.atomic():
                ner_to_update.update(jsonDict = path_final, jsondict_str = str_dict, jsonNER = config_obj.json.name, jsonner_str = config_obj.json_str, entity_model_current = str_em)
            
        # Return JSON response to requester
        return JsonResponse({'cod':0 , 'res': "ok"})

