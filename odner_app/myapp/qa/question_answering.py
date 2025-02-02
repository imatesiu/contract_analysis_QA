"""
This is a Python script that defines a Django class-based view to perform question-answering 
using the Hugging Face Transformers library. The view uses the REST framework to handle HTTP requests and 
returns a JSON response containing the highlighted text and answer.

The `JSONToDict` function is a helper function that reads a JSON file and returns its contents as a 
dictionary.

The `highlight_entities` function takes a text and a dictionary of entities as input and returns a 
tuple containing the highlighted text, color codes for each entity, and a list of the entities. 
The function loops through each entity in the dictionary, generates a unique inline style for the entity, 
and creates a span tag with the inline style for each word in the entity's list. The resulting HTML string is returned as the highlighted text.

The `QA` class-based view is a subclass of `generics.CreateAPIView` that overrides the `post` method. 
The `post` method reads the question, model name, and context from the request data, 
creates a question-answering pipeline using the specified model, uses the pipeline to answer the question, highlights any entities 
in the context that match the answer using the `highlight_entities` 
function, and returns a JSON response containing the highlighted text and answer.

The `qa` pipeline is created using the `pipeline` function from the Hugging Face Transformers library, 
which creates a question-answering pipeline using the specified model. The `result` variable is a 
dictionary containing the answer, start and end indices of the answer in the context, 
and a score representing the confidence of the answer. 
The answer is extracted from the `result` dictionary and returned in the JSON response along with the 
highlighted text.
"""


import json
import spacy
from django.http import JsonResponse
from rest_framework import generics
from transformers import pipeline
import os
import logging
import re
import threading
from functools import wraps
import requests
import urllib

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
def highlight_entities(text, start_pos, end_pos):
    """
    Highlight the specified range of the entity in the text with a different color

    :param text: The input text to highlight
    :param answer: The entity to highlight
    :param start_pos: The start position of the entity in the text
    :param end_pos: The end position of the entity in the text
    :return: Highlighted text
    """

    # Generate a unique inline style for the entity
    style = "background-color: red;"

    # Replace the specified range with the highlighted version
    highlighted_text = f"{text[:start_pos]}<span style='{style}'>{text[start_pos:end_pos]}</span>{text[end_pos:]}"

    # Return the highlighted text
    return highlighted_text



class QA(generics.CreateAPIView):
    """
        Class-based view to perform question - answering task
    """

    lock = threading.RLock()

    def post(self, request, *args, **kwargs):
        """
        :param request: The HTTP request object.
        :type request: HttpRequest
        :return: A JSON response containing the highlighted text and answer.
        :rtype: JsonResponse
        """
        logger = logging.getLogger('appLog')
        highlight_text = ''  # Initialize highlight text to an empty string.

        # Get the question, model name, and context from the request data.
        question = request.data.get('question', None)
        model_name = request.data.get('model', None)
        context = request.data.get('text', None)
        #context = context.replace("b\'","").replace("\'","")
        
        #style = "background-color: red;"

        # If no question was provided, return an error message.
        if question == None:
            return JsonResponse({'high': "Nessuna domanda inviata", })
        
        nlp = spacy.load("en_core_web_md")
        doc = nlp(context)
        highlight_texts = ""
        answers = []
        scores = []
        sentes = []
        for element in doc.sents:
            logger.error(element)
            text = str(element)
            sentes.append(text)

        for textx in sentes:  
            with self.lock:
            # Create a question-answering pipeline using the specified model.
             qa1 = pipeline("question-answering", model=model_name, n_process=-1 , disable=[ 'parser', 'lemmatizer', 'tagger','tok2vec'])

            # Use the pipeline to answer the question.
             result1 = qa1(question=question, context=textx)
            #logger.error(result1)
             logger.error("CIAONE")
            # Extract the answer from the result.
             answer = result1['answer']

             score = result1['score']

             start_pos = result1['start']
             end_pos = result1['end']
            # Highlight any entities in the context that match the answer.
             #logger.error(type(text))
             #logger.error(len(text))
             logger.error(textx)

             #highlighted_text = text[:start_pos]+"<span style=\'"+style+"\'>"+text[start_pos:end_pos]+"</span>"+text[end_pos:]

             highlight_text2 = highlight_entities(textx, start_pos, end_pos)
             #logger.error(highlight_text2)
             #logger.error(start_pos)
             #logger.error(end_pos)
             answers.append(answer)
             scores.append(score)
             highlight_texts = highlight_texts + highlight_text2
            #break
            #logger.error(highlight_texts)


	

        logger.error("CIAO555")
        with self.lock:
            # Create a question-answering pipeline using the specified model.
            qa = pipeline("question-answering", model=model_name)

            # Use the pipeline to answer the question.
            result = qa(question=question, context=context)

        # Extract the answer from the result.
        answer = result['answer']

        score = result['score']

        start_pos = result['start']
        end_pos = result['end']
        logger.error(start_pos)
        logger.error(end_pos)
        logger.error("end")
        # Highlight any entities in the context that match the answer.
        highlight_text = highlight_entities(context, start_pos, end_pos)

        # Return a JSON response containing the highlighted text and answer.
        return JsonResponse({'high_qa': highlight_texts, 'answer': answer, 'score': score, 'answers': answers, 'scores': scores, 'sentes' : sentes})




