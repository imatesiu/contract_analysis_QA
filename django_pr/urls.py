"""
    This code is defining the URL patterns for a Django application, which includes various endpoints for different functionalities of the application. The path function from django.urls is used to define the URLs, 
    and each URL is associated with a view class that handles the corresponding request.

    The URLs defined in this code include:

    - /api/: This is the base URL for accessing the Django REST Framework.
    - /api/pdf-upload/: This URL is used for uploading a PDF file and is associated with the PDFUploadView class.
    - /api/word-upload/: This URL is used for uploading a Word document and is associated with the DOCUploadView class.
    - /api/xlsx-upload/: This URL is used for uploading an Excel file and is associated with the XLSXUploadView class.
    - /api/update-text/: This URL is used for updating the text of a document and is associated with the EditTXTView class.
    - /api/load-config/: This URL is used for loading the configuration and is associated with the LoadConfig class.
    - /api/filter/: This URL is used for filtering named entities and is associated with the FilterView class.
    - /api/get-config/: This URL is used for getting the configuration and is associated with the GetConfig class.
    - /api/qa/: This URL is used for performing question-answering and is associated with the QA class.
    - /api/save-question/: This URL is used for saving a question and is associated with the Save class.
    - /api/change-cnf/: This URL is used for changing the configuration and is associated with the configChange class.
    - /api/delete-entities/: This URL is used for deleting named entities and is associated with the DeleteEntities class.

"""


# Import the necessary modules and classes from the application's files
from django.urls import path, include
from myapp.upload_file import pdf_upload, docx_upload, xlsx_upload  # Classes for uploading a document, extracting its text, and translating it (from Italian to English)
from myapp.edit_file import edit_file  # Class for editing the text
from myapp.load_config import loadConfig  # Class for loading the configuration
from myapp.filter import filterNER  # Class for filtering named entities
from myapp.load_config import getConfig  # Class for getting the configuration
from myapp.qa import question_answering  # Class for performing question-answering
from myapp.save_q import saveQuestion  # Class for saving a question
from myapp.load_config import changeConfig  # Class for changing the configuration
from myapp.load_config import deleteEn  # Class for deleting named entities

# Define the schema URLs for the application
# Each URL is connected to a view class that handles requests
urlpatterns = [
    path('api/', include('rest_framework.urls')),  # URL for accessing the Django REST Framework
    path('api/pdf-upload/', pdf_upload.PDFUploadView.as_view(), name='pdf-upload'),  # URL for uploading a PDF file
    path('api/word-upload/', docx_upload.DOCUploadView.as_view(), name='word-upload'),  # URL for uploading a Word document
    path('api/xlsx-upload/', xlsx_upload.XLSXUploadView.as_view(), name='xlsx-upload'),  # URL for uploading an Excel file
    path('api/update-text/', edit_file.EditTXTView.as_view(), name='update-text'),  # URL for updating the text of a document
    path('api/load-config/', loadConfig.LoadConfig.as_view(), name='load-config'),  # URL for loading the configuration
    path('api/filter/', filterNER.FilterView.as_view(), name='filter'),  # URL for filtering named entities
    path('api/get-config/', getConfig.GetConfig.as_view(), name='get-config'),  # URL for getting the configuration
    path('api/qa/', question_answering.QA.as_view(), name='qa'),  # URL for performing question-answering
    path('api/save-question/', saveQuestion.Save.as_view(), name='save-q'),  # URL for saving a question
    path('api/change-cnf/', changeConfig.configChange.as_view(), name='change-cnf'),  # URL for changing the configuration
    path('api/delete-entities/', deleteEn.DeleteEntities.as_view(), name='del-en'),  # URL for deleting named entities
]
