"""
The script defines the following functions:

    - JSONToDict(): a function that converts a JSON file to a dictionary object.
    - highlight_entities(): a function that takes the input text, entity dictionary, and number of entities as input, and returns a tuple containing the highlighted text, 
                        color codes for each entity, and a list of the entities. 
                        The function generates a unique inline style for each entity, creates a span tag with the inline style for each word in the entity's list, and returns the HTML string.
    
The script defines the following class:

    - FilterView(): a class that inherits from the generics.CreateAPIView class. 
    This class contains a post() method that handles HTTP POST requests to filter the text and highlight entities.

    The post() method retrieves the file path of the text document and the selected entities from the request data. 
    It then retrieves the corresponding JSON file from the NER model, filters out the selected entities from the JSON dictionary, 
    and passes the filtered dictionary and text to the highlight_entities() function to highlight the entities in the text. 
    Finally, it returns the highlighted text, color codes for each entity, and a list of the entities as a JSON response.

"""


# import libraries
import json
import re

from django.http import JsonResponse
from myapp.models import NER
from rest_framework import generics

# function to convert JSON file to dictionary
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

def highlight_entities(text, entity_dict):
    """
    Highlight the entities in the text with different colors

    :param text: The input text to highlight
    :param entity_dict: A dictionary containing the entities and their corresponding words
    :return: A tuple containing the highlighted text, color codes for each entity, and a list of the entities
    """
    # Define colors for highlighting
    html_colors = [
        '#FFFFE0', '#90EE90', '#E0FFFF', '#FFE4E1', '#AFEEEE', '#E6E6FA', '#D3D3D3',
        '#F0FFF0', '#F0E68C', '#B0E0E6', '#FFDAB9', '#ADD8E6', '#FFB6C1', '#C0C0C0',
        '#FFF5EE', '#F5F5DC', '#FFF0F5', '#EEE8AA', '#FFA07A', '#87CEFA', '#98FB98',
        '#F0F8FF', '#778899', '#FFFFF0', '#FFFACD', '#FFE4B5', '#FDF5E6', '#FFEFD5',
        '#FFDAB9', '#D8BFD8', '#B0C4DE'
    ]

    colors = []
    name_entities = []

    # Loop through each entity in the dictionary
    for i, (entity, words) in enumerate(entity_dict.items()):
        # Generate a unique inline style for the entity
        style = f"background-color: {html_colors[i % len(html_colors)]};"

        colors.append(html_colors[i % len(html_colors)])
        name_entities.append(entity)

        # Create a span tag with the inline style for each word in the entity's list
        for word in words:
            text = text.replace(word, f"<span style='{style}'>{word}</span>")

    # Return the HTML string
    return text, colors, name_entities


class FilterView(generics.CreateAPIView):
    """
    Class-based view to filter the text and highlight entities
    """

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to filter the text and highlight entities

        :param request: The incoming request
        :type request: HttpRequest
        :return: The JSON response containing the highlighted text, color codes for each entity, and a list of the entities
        :rtype: JsonResponse
        """
        highlight_text = ''

        txt_file_path = request.data.get('file_txt_path', None)

        # Replace the URL encoded Windows path with a proper path
        txt_file_path = re.sub("/C%3A", "C:", txt_file_path)

        text = request.data.get('text', None)

        entities = []

        entities = request.data.get('selectedEn', None)

        ner_obj = None

        ner_obj = NER.objects.filter(title=txt_file_path).first()

        json_file = ner_obj.jsonDict.name

        dict = JSONToDict(json_file)

        # Filter out the selected entities from the dictionary
        sub_dict = {key: dict[key] for key in entities if key in dict}

        col = []
        ent = []

        # Highlight the text based on the sub-dict
        highlight_text, col, ent = highlight_entities(text,sub_dict)    

        # Return JSON response to requester
        return JsonResponse({'high': highlight_text, 'colors': col, 'ent': ent})
