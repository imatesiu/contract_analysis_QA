"""
This is a Django REST Framework view that defines an endpoint for loading configuration for Named Entity Recognition (NER) in a text. 
The endpoint receives a POST request with the following parameters: file_txt_path, language, text, and f_up (an uploaded file). 
The view performs the following steps:

Check if an NER object already exists for the given file_txt_path. If it does, the object is serialized and returned as a JSON response.
If the NER object does not exist, the view performs NER on the given text using the specified language. 
The resulting named entities are stored in a dictionary.
The view creates a JSON file from the dictionary and saves it in a directory named JSONDicts.
The view retrieves a base configuration JSON file from a directory named json_configs.
The view converts both the JSON files to strings.
The view updates the NER object with the paths to the created JSON files and the base configuration file, the input text, and the specified language.
The updated NER object is serialized and returned as a JSON response.
The view assumes that the spacy models for the specified languages ('en' and 'it') are installed and that the Django app has models named NER and Config. The view also assumes 
that there are directories named json_configs and JSONDicts in the same directory as the view file. The view uses several helper functions to convert dictionaries to JSON files and vice versa, and to convert JSON files to strings.

"""


from django.http import JsonResponse
from rest_framework import generics
from myapp.models import NER, Config
from myapp.serializers.config_serializer import NERserializer
import json
import os
import spacy
import re
from django.db import transaction
import threading
from functools import wraps
from transformers import pipeline
import spacy_transformers

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

class LoadConfig(generics.CreateAPIView):

    lock = threading.RLock()

    def post(self, request, *args, **kwargs):
        """
        Endpoint to load configuration for NER.

        :param request: HTTP request object.
        :type request: HttpRequest object.

        :returns: JSON response object.
        :rtype: JsonResponse object.
        """

        # Get input data from the request.
        txt_file_path = request.data.get('file_txt_path', None)
        language = request.data.get('language', None)
        text = request.data.get('text', None)
        uploaded_file = request.data.get('f_up')

        # Fix file path format for Windows.
        txt_file_path = re.sub("/C%3A", "C:", txt_file_path)

        cartella = os.path.dirname(os.path.abspath(__file__)) + '/JSONDicts/'

        if not os.path.exists(cartella):
            # Crea la cartella
            os.makedirs(cartella)

        # Check if the NER object already exists.
        ner_obj = NER.objects.filter(title=txt_file_path).first()

        # Initialize variables.
        file_config = None
        ner_str = ""

        path = txt_file_path.split('/')[-1]
        path = path[:-6] 

        # Get file paths for config and JSON dictionary.
        if language == 'en':
            file_config = os.path.dirname(os.path.abspath(__file__)) + '\json_configs' + '\\base-en.json'
            file_path_json_dict = os.path.dirname(os.path.abspath(__file__)) + '/JSONDicts/' + path + 'base-en' + '.json'
        else:
            file_config = os.path.dirname(os.path.abspath(__file__)) + '\json_configs' + '\\base-it.json'
            file_path_json_dict = os.path.dirname(os.path.abspath(__file__)) + '/JSONDicts/' + path + 'base-it' + '.json'


        if ner_obj is None:
            # Run NER and create JSON file.
            dict = ner(text, language)

            # Convert dict to JSON and write to file.
            DictToJSON(dict, file_path_json_dict)

            # Convert config and JSON dictionary files to strings.
            ner_str = json_to_string(file_config)
            dict_str = json_to_string(file_path_json_dict)

            # Get the current model and update the NER object.
            file_config = re.sub("/C%3A", "C:", file_config)
            current_model = Config.objects.filter(title=file_config).first().entity_model
            

            with transaction.atomic():
                ner_new = NER.objects.create(
                title=txt_file_path,
                raw_file=uploaded_file,
                jsonDict=file_path_json_dict,
                jsonNER=file_config,
                language=language,
                jsonner_str=ner_str,
                jsondict_str=dict_str,
                entity_model_current=current_model
            )
                ner_new.save()

            # Serialize the NER object and return a JSON response.
            return JsonResponse(NERserializer(ner_new).data)

        else:
            # Serialize the existing NER object and return a JSON response.
            if ner_obj.jsonNER.name != file_config: # No base configuration

                dict_json = JSONToDict(ner_obj.jsonDict.name)

                config_obj = Config.objects.filter(title = ner_obj.jsonNER.name).first()

                if config_obj != None:

                    dict_question = JSONToDict(config_obj.json.name)

                    em = json.loads(config_obj.entity_model)


                    text = ""

                    with self.lock:
                        with open(txt_file_path,"r") as out:
                            text = out.read()
                    

                    for key in em.keys():
                        if (key not in dict_json.keys()) & (em[key] != "Spacy"):

                            question = dict_question[key]


                            with self.lock:

                                qa = pipeline("question-answering", model=em[key])

                                result = qa(question=question, context=text)

                            answer = result['answer']

                            dict_json[key] = []

                            dict_json[key].append(answer)

                    # Write the modified dictionary back to the JSON file
                    DictToJSON(dict_json, ner_obj.jsonDict.name)

                    str_dict = json_to_string(ner_obj.jsonDict.name)

                    str_em = json.dumps(em)

                    str_ner = config_obj.json_str

                    json_ner = config_obj.json

                    ner_to_update = NER.objects.select_for_update().filter(title=txt_file_path).all()

                    # Update NER object
                    with transaction.atomic():
                        ner_to_update.update(
                        jsondict_str=str_dict, jsonNER=json_ner, jsonner_str=str_ner, entity_model_current=str_em)
                    
                    ner_to_update = NER.objects.filter(title=txt_file_path).first()
                    ner_to_update.save
                    return JsonResponse(NERserializer(ner_to_update).data)

                else:
                    # Run NER and create JSON file.
                    dict = ner(text, language)

                    # Convert dict to JSON and write to file.
                    DictToJSON(dict, file_path_json_dict)

                    # Convert config and JSON dictionary files to strings.
                    ner_str = json_to_string(file_config)
                    dict_str = json_to_string(file_path_json_dict)

                    # Get the current model and update the NER object.
                    current_model = Config.objects.filter(title=file_config).first().entity_model
                    file_config = re.sub("/C%3A", "C:", file_config)

                    ner_to_update = NER.objects.select_for_update().filter(title=txt_file_path).all()

                    with transaction.atomic():
                        ner_to_update.update(
                        
                        jsonDict=file_path_json_dict,
                        jsonNER=file_config,
                        
                        jsonner_str=ner_str,
                        jsondict_str=dict_str,
                        entity_model_current=current_model
                    )

                    ner_to_update =   NER.objects.filter(title=txt_file_path).first()
                    
                    return JsonResponse(NERserializer(ner_to_update).data)
            else:
                return JsonResponse(NERserializer(ner_obj).data)
              
                
            

        

      




       
    
    



