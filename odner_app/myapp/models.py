"""
The code defines six Django models to store different types of data:

1. `PDF`: A model for PDF files. It has fields for storing the title of the document, the PDF file itself, and the extracted and translated text in Italian and English. It also has fields for storing the processed Italian and English text in `.txt` format.

2. `DOC`: A model for DOC files. It has fields for storing the title of the document, the DOC file itself, and the extracted and translated text in Italian and English. It also has fields for storing the processed Italian and English text in `.txt` format.

3. `XLSX`: A model for XLSX files. It has fields for storing the title of the document, the XLSX file itself, and the extracted and translated text in Italian and English. It also has fields for storing the processed Italian and English text in `.txt` format.

4. `EditText`: A model for edited text. It has fields for storing the title of the object, the edited text, and the file for saving the edited object in `.txt` format.

5. `NER`: A model for storing information about Named Entity Recognition (NER) data. It has fields for storing the title of the NER data, the original raw data file, a personal dictionary JSON file, the configuration JSON file, the current configuration's `json_str` and `ner_str`, the language of the NER data, and the current entity model JSON string.

6. `Config`: A model for storing information about a configuration file. It has fields for storing the title/path of the configuration file, the configuration JSON file, the current configuration's `json_str`, the language of the configuration file, and the entity model JSON string.

"""


from django.db import models


class PDF(models.Model):
    """
    Model for PDF files.
    """

    title = models.CharField(max_length=200)  # title of the document
    pdf_file = models.FileField(
        upload_to='myapp/upload_file//myapp_file/pdfs/')  # file to be processed

    # extracted and translated Italian text
    pdf_text_it = models.TextField(blank=True, null=True, max_length=None)
    # extracted and translated English text
    pdf_text_en = models.TextField(blank=True, null=True, max_length=None)

    # .txt file of the processed Italian text
    txt_file_pdf_it = models.FileField(blank=True)
    # .txt file of the processed English text
    txt_file_pdf_en = models.FileField(blank=True)

    def __str__(self):
        """
        Returns a string representation of the object.
        """
        return self.title


class DOC(models.Model):
    """
    Model for DOC files.
    """

    title = models.CharField(max_length=200)
    doc_file = models.FileField(
        upload_to='myapp/upload_file//myapp_file/docs/')

    # extracted and translated Italian text
    docx_text_it = models.TextField(blank=True, null=True, max_length=None)
    # extracted and translated English text
    docx_text_en = models.TextField(blank=True, null=True, max_length=None)

    # .txt file of the processed Italian text
    txt_file_docx_it = models.FileField(blank=True)
    # .txt file of the processed English text
    txt_file_docx_en = models.FileField(blank=True)

    def __str__(self):
        """
        Returns a string representation of the object.
        """
        return self.title


class XLSX(models.Model):
    """
    Model for XLSX files.
    """

    title = models.CharField(max_length=200)
    xlsx_file = models.FileField(
        upload_to='myapp/upload_file//myapp_file/xlsx/')

    # extracted and translated Italian text
    xlsx_text_it = models.TextField(blank=True, null=True, max_length=None)
    # extracted and translated English text
    xlsx_text_en = models.TextField(blank=True, null=True, max_length=None)

    # .txt file of the processed Italian text
    txt_file_xlsx_it = models.FileField(blank=True)
    # .txt file of the processed English text
    txt_file_xlsx_en = models.FileField(blank=True)

    def __str__(self):
        """
        Returns a string representation of the object.
        """
        return self.title


class EditText(models.Model):
    """
    Model for edited text.
    """

    title = models.CharField(max_length=200)  # title of the object
    text_edited = models.TextField(
        blank=True, null=False, max_length=None)  # edited text
    # file for saving the edited object
    txt_file_edited = models.FileField(blank=True)

    def __str__(self):
        """
        Returns a string representation of the object.
        """
        return self.title

    
class NER(models.Model):
    """
    A Django model to store information about Named Entity Recognition (NER) data.
    """
    title = models.CharField(max_length=200)  # Title of the NER data
    raw_file = models.FileField(blank=True)  # Original raw data file
    jsonDict = models.FileField(blank=True)  # Personal dictionary JSON file
    # Configuration JSON file -> initially base-it/en.json
    jsonNER = models.FileField(blank=True)
    # Current configuration's json_str
    jsonner_str = models.TextField(blank=True)
    # Current configuration's ner_str
    jsondict_str = models.TextField(blank=True)
    language = models.CharField(max_length=50)  # Language of the NER data
    entity_model_current = models.TextField(
        blank=True, null=True)  # Current entity model JSON str

    def __str__(self):
        """
        Returns a string representation of the NER data object.
        """
        return self.title


class Config(models.Model):
    """
    A Django model to store information about a configuration file.
    """
    title = models.CharField(
        max_length=200)  # Title/path of the configuration file
    # Configuration JSON file -> initially base-it/en.json
    json = models.FileField(blank=True)
    json_str = models.TextField(blank=True)  # Current configuration's json_str
    # Language of the configuration file
    language = models.CharField(max_length=50)
    entity_model = models.TextField(
        blank=True, null=True)  # Entity model JSON str

    def __str__(self):
        """
        Returns a string representation of the Config object.
        """
        return self.title
