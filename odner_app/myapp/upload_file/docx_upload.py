from django.http import JsonResponse # importazione libreria per gestire richieste http utilizzando JSON come formato per la serializzazione e deserializzazione dei dati e per inviare al richiedente il testo processato
from rest_framework import generics 
from myapp.models import DOC # importazione modello per documenti MSWord (vedi django_pr/models.py)
from myapp.serializers.docx_serializer import DOCSerializer # importazione serializzatore JSON del modello (vedi my_app/serializers/docx_serializer.py)
import threading
import re # libreria per operare con REGEX
import os # libreria per operare all'interno del SO -> recuperare path_file per salvataggio dei file creati durante il processo
import docx2txt # libreria per estrarre il testo dal documento .docx
from deep_translator import GoogleTranslator
from django.db import transaction

def extraction(to_extract):
        """
        Extract text from the given PDF and clean it up.
        
        :param to_extract: path to the PDF file
        :return: cleaned text as a string
        """
        text = docx2txt.process(to_extract) # estrazione testo dal file .docx

        towrite = ""

        # pulizia e riformattazione del testo
        for line in text:

            if(line == '\n') | (line == '\r') | (line == '\r'):
                towrite = towrite + ' '
            else:
                towrite = towrite + line

        pattern = r'(\w)-\s*(\w)' 
        replacement = r'\1\2'
        towrite = re.sub(pattern, replacement, towrite) # aggiustamenti sul testo per gestire \n utilizzando REGEX

        towrite = re.sub(' +', ' ', towrite) # eliminazione spazi superflui sempre tramite REGEX

        return towrite
    
def translate(towrite):
        """
        Translate text from Italian to English using Google Translate API.
    
        :param towrite: text to translate
        :return: translated text as a string
        """
        result = ""

        parts = towrite.split('.')

        for p in parts:
            if len(p) > 5:
                tmp = GoogleTranslator(source='it', target='en').translate(text=p)
                result = result + tmp + '.'

            else:
                result += p
        return result


# classe per gestire l'upload di un file .docx, estrarne il testo, tradurlo e infine inviare il risultato sotto forma di JSON al richiedente

class DOCUploadView(generics.CreateAPIView):
    """
    View for uploading a DOCX file and saving its extracted and translated text.
    """

    lock = threading.RLock()

    def post(self, request, *args, **kwargs):
        """
        Process the uploaded DOCX file and save its extracted and translated text.
        
        :param request: HTTP request.
        :type request: HttpRequest.
        :return: HTTP response.
        :rtype: JsonResponse.
        """
    

        uploaded_file = request.FILES.get('file', None)

        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'})

        language = request.data.get('language', None)

        txt_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'txt_files/docx/'
        )

        if not os.path.exists(txt_dir):
            os.makedirs(txt_dir)

        doc_new = None

        file_name = uploaded_file.name

        file_path = os.path.join(txt_dir, file_name[:-5]+'-' + language + '.txt')

        file_path_docx = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'myapp_file/docs/', file_name)
        
        if not(os.path.exists(file_path_docx)):
            if(language == 'it'): #estrazione in italiano

                with self.lock:
                    with open(file_path, "wb") as out:

                        towrite = extraction(uploaded_file)
                        out.write(towrite.encode('utf-8'))
                
                doc_new = DOC.objects.filter(title = file_path_docx).first()

                if doc_new:
                    queryset =  DOC.objects.select_for_update().filter(title = file_path_docx).all()

                    with transaction.atomic():
                        queryset.update(
                            title=file_path_docx, doc_file=uploaded_file, docx_text_it=towrite, docx_text_en=None, txt_file_docx_it=file_path, txt_file_docx_en=None)
                else:
                    with transaction.atomic():
                        doc_new = DOC.objects.create(
                            title=file_path_docx, doc_file=uploaded_file, docx_text_it=towrite, docx_text_en=None, txt_file_docx_it=file_path, txt_file_docx_en=None)
                        doc_new.save()

                serializer = DOCSerializer(doc_new)

                return JsonResponse(serializer.data)   


            else:
                with self.lock:
                    with open(file_path, "wb") as out:

                        towrite = extraction(uploaded_file)
                        towrite = translate(towrite)
                        out.write(towrite.encode('utf-8'))

                if doc_new:
                    queryset = DOC.objects.select_for_update().filter(title=file_path_docx).all()
                     
                    with transaction.atomic():
                        queryset.update(
                            title=file_path_docx, doc_file=uploaded_file, docx_text_it=None, docx_text_en=towrite, txt_file_docx_it=None, txt_file_docx_en=file_path)
                else:
                    with transaction.atomic():
                        doc_new = DOC.objects.create(
                            title=file_path_docx, doc_file=uploaded_file, docx_text_it=None, docx_text_en=towrite, txt_file_docx_it=None, txt_file_docx_en=file_path)
                        doc_new.save()
                
                serializer = DOCSerializer(doc_new)

                return JsonResponse(serializer.data)               

        else:
            if os.path.exists(file_path):  # il file .txt è già stato creato
                docx = DOC.objects.filter(title=file_path_docx).first()
                serializer = DOCSerializer(docx)
                return JsonResponse(serializer.data)
            else:
                if(language == 'it'):
                    with self.lock:
                        with open(file_path, "wb") as out:

                            towrite = extraction(uploaded_file)
                            out.write(towrite.encode('utf-8'))

                    # recupero record
                    queryset = DOC.objects.select_for_update().filter(title=file_path_docx).all()

                    with transaction.atomic():
                        queryset.update(docx_text_it = towrite, txt_file_docx_it = file_path)    
                    
                    docx = DOC.objects.filter(title=file_path_docx).first()

                    #serializzazione
                    serializer = DOCSerializer(docx)

                    # return jsonResponse
                    return JsonResponse(serializer.data)

                else:
                    with self.lock:
                        with open(file_path, "wb") as out:

                            towrite = extraction(uploaded_file)
                            towrite = translate(towrite)
                            out.write(towrite.encode('utf-8'))

                    # recupero record

                    queryset = DOC.objects.select_for_update().filter(title=file_path_docx).all()

                    with transaction.atomic():
                        queryset.update(docx_text_en = towrite, txt_file_docx_en = file_path)
                    
                    docx = DOC.objects.filter(title=file_path_docx).first()

                    #serializzazione
                    serializer = DOCSerializer(docx)

                    # return jsonResponse
                    return JsonResponse(serializer.data)
