"""
The functions are defined as follows:

    - ner(txt_to_ner, language): performs Named Entity Recognition (NER) on text using Spacy and returns the named entities as a dictionary.

    - JSONToDict(filename): converts a JSON file to a dictionary and returns the dictionary.

    - json_to_string(file_path): converts a JSON string to a JSON object and returns the JSON object.

    - DictToJSON(my_dict, filename): converts a dictionary to a JSON file and saves it to disk.

The class EditTXTView is a Django API endpoint that allows users to upload a text file, edit its contents, and perform NER on the edited text. The class includes a post method that processes the uploaded file and text, saves the edited text to disk, updates the relevant database record, performs NER on the edited text, and returns a JSON response containing the edited text. The post method uses the functions defined above to perform its tasks.

The class EditSerializer is used to serialize the EditText object, which is used to store the edited text in the database.

"""

# import libraries
import json
import spacy_transformers
import re
import os
import spacy
from django.http import JsonResponse
from rest_framework import generics
from transformers import pipeline
from myapp.models import DOC, EditText, NER, PDF, XLSX
from myapp.serializers.edit_serializer import EditSerializer
from django.db import transaction
import threading
from functools import wraps


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


class EditTXTView(generics.CreateAPIView):
    
    """ 
    Class-based view for edit the text

    """

    lock = threading.Lock()
    
    def post(self, request, *args, **kwargs):

        """
            Handle the POST request to edit the text and perform NER and question-answering on the modified text (if there was a previously associated configuration)

            :param request: The incoming request 
            :type request: HttpRequest
            :return: The JSON response containing the text edited
            :rtype: JsonResponse
        """

        # Get text file and edited text from request data
        txt_file = request.data.get('file_toEdit')  # Retrieve .txt file containing the text to edit
        txt_edited = request.data.get('text_toEdit')  # Retrieve text to edit

        # Replace file path string pattern
        txt_file = re.sub("/C%3A", "C:", txt_file)

        # Get file source from request data
        file_up = request.data.get('file_source')

        with self.lock:
            # Write edited text to the .txt file
            with open(txt_file, 'wb') as out:
                out.write(txt_edited.encode('utf-8'))

        # Update model parameters based on file type and language
        l = request.data.get('language')

        query_pdf = PDF.objects.select_for_update().filter(title=file_up).all()
        query_doc = DOC.objects.select_for_update().filter(title=file_up).all()
        query_xlsx = XLSX.objects.select_for_update().filter(title=file_up).all()

        with transaction.atomic():
            if file_up[-4:] == '.pdf':
                if l == 'it':
                    query_pdf.update(
                        pdf_text_it=txt_edited, txt_file_pdf_it=txt_file)
                else:
                    query_pdf.update(
                        pdf_text_en=txt_edited, txt_file_pdf_en=txt_file)

            elif file_up[-5:] == '.docx':
                if l == 'it':
                    query_doc.update(
                        docx_text_it=txt_edited, txt_file_docx_it=txt_file)
                else:
                    query_doc.update(
                        docx_text_en=txt_edited, txt_file_docx_en=txt_file)

            else:
                if l == 'it':
                    query_xlsx.update(
                        xlsx_text_it=txt_edited, txt_file_xlsx_it=txt_file)
                else:
                    query_xlsx.update(
                        xlsx_text_en=txt_edited, txt_file_xlsx_en=txt_file)

        # Perform named entity recognition (NER) on edited text
        ner_obj = NER.objects.filter(title=txt_file).first()

        if ner_obj is not None:
            
            dict = ner(txt_edited,l)

            # Convert JSON object to dictionary
            tmp = ner_obj.jsonDict.name
            ner_dict = JSONToDict(ner_obj.jsonNER.name)
            
            model = json.loads(ner_obj.entity_model_current)

            # Iterate through entity model keys
            for key in model.keys():
                if model[key] != 'Spacy':
                    # Get model name and question from NER dictionary
                    model_name = model[key]
                    question = ner_dict[key]

                    # Perform question answering on edited text
                    qa = pipeline("question-answering", model=model_name)
                    result = qa(question=question, context=txt_edited)

                    # Extract answer from result
                    answer = result['answer']

                    # Add answer to dictionary
                    dict[key] = []
                    dict[key].append(answer)

            # Convert dictionary to JSON object
            DictToJSON(dict, tmp)
            dict_str = json_to_string(tmp)
            str_model = json.dumps(model)

            # Update NER object with new JSON dictionary

            queryset = NER.objects.select_for_update().filter(title=txt_file).all()

            with transaction.atomic():
                queryset.update(jsondict_str=dict_str, jsonDict=tmp, entity_model_current = str_model)

            # Update base configuration
            
            path_base = ner_obj.jsonDict.name.split('/')[:-1]
            name_dict = ner_obj.jsonDict.name.spli('/')[-1]
            path = ""
            for p in path_base:
                path +=p+'/'
            
            path+=name_dict+'-base-'+ner_obj.language+'.json'
            
            dict_base = JSONToDict(os.path.abspath(path))

            dict_base = ner(txt_edited,ner_obj.language)

            DictToJSON(dict_base)

            # Delete the others jsonDict file that don't corresponde anymore to the extracted text (they will be reloaded when the user will change the configuration)

            directory = os.path.dirname(os.path.abspath(__file__))+'\JSONDicts/'

            # Iterate over all the files in the directory 'JSONDicts'
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    path_current = os.path.abspath(os.path.join(root, filename))

                    
                    if path_current != path & path_current!=ner_obj.jsonDict.name:
                        with self.lock:
                            # Delete file
                            if os.path.isfile(path_current):
                                os.remove(path_current)

        # Create EditText object to make data persistent
        with transaction.atomic():
            txt_new = EditText.objects.create(title=txt_file, text_edited=txt_edited, txt_file_edited=txt_file)
            txt_new.save()

        # Serialize EditText object to JSON
        serializer = EditSerializer(txt_new)

        # Return JSON response to requester
        return JsonResponse(serializer.data)
