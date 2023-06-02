from django.http import JsonResponse # importazione libreria per gestire richieste http utilizzando JSON come formato per la serializzazione e deserializzazione dei dati e per inviare al richiedente il testo processato
from rest_framework import generics
from myapp.models import XLSX # importazione modello per documenti EXCEL .xlsx (vedi django_pr/models.py)
from myapp.serializers.xlsxs_erializers import XLSXSerializer # importazione serializzatore JSON del modello (vedi my_app/serializers/xlsx_serializer.py)
import threading
import openpyxl # libreria per estrarre il testo dal documento .xlsx
from deep_translator import (GoogleTranslator) # libreria per la traduzione del testo all'interno del file .txt creato dopo l'estrazione del testo del documento
import re # libreria per operare con REGEX
import os # libreria per operare all'interno del SO -> recuperare path_file per salvataggio dei file creati durante il processo
from django.db import transaction

# classe per gestire l'upload di un file .xlsx, estrarne il testo, tradurlo e infine inviare il risultato sotto forma di JSON al richiedente
def extraction(to_extract):
        """
        Extract text from the given PDF and clean it up.
        
        :param to_extract: path to the PDF file
        :return: cleaned text as a string
        """
        workbook = openpyxl.load_workbook(to_extract)

        worksheet = workbook.active

        towrite = ""

        for row in worksheet.iter_rows():
            for cell in row:
                towrite += ' ' + str(cell.value)  # estrazione testo
                # eliminazione spazi superflui sempre tramite REGEX
                towrite = re.sub(' +', ' ', towrite)
                towrite = towrite + '\n'   
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
                tmp = GoogleTranslator(
                    source='it', target='en').translate(text=p)
                result = result + tmp + '.'
                                
            else:
                result += p

        return result

class XLSXUploadView(generics.CreateAPIView):
    """
    View for uploading a XLSX file and saving its extracted and translated text.
    """

    lock = threading.RLock()

    def post(self, request, *args, **kwargs):
        """
        Process the uploaded XLSX file and save its extracted and translated text.
    
        :param request: HTTP request.
        :type request: HttpRequest.
        :return: HTTP response.
        :rtype: JsonResponse.
        """

        uploaded_file = request.FILES.get('file', None)

        xlsx_new = None

        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'})

        language = request.data.get('language', None)

        txt_dir = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), 'txt_files/xlsx/')

        if not os.path.exists(txt_dir):
            os.makedirs(txt_dir)

        file_name = uploaded_file.name

        file_path = os.path.join(txt_dir, file_name[:-5]+'-' + language + '.txt')

        file_path_xlsx = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'myapp_file/xlsx/', file_name)
        
        if not(os.path.exists(file_path_xlsx)):
            if(language == 'it'): #estrazione in italiano
                    
                with self.lock:

                    with open(file_path, "wb") as out:

                        towrite = extraction(uploaded_file)
                        out.write(towrite.encode('utf-8'))

                xlsx_new = XLSX.objects.filter(title = file_path_xlsx).first()

                if xlsx_new:
                    queryset = XLSX.objects.select_for_update().filter(title = file_path_xlsx).all()
                    with transaction.atomic():
                        queryset.update(
                            title=file_path_xlsx, xlsx_file=uploaded_file, xlsx_text_it=towrite, xlsx_text_en=None, txt_file_xlsx_it=file_path, txt_file_xlsx_en=None)
                else:
                    with transaction.atomic():
                        xlsx_new = XLSX.objects.create(
                            title=file_path_xlsx, xlsx_file=uploaded_file, xlsx_text_it=towrite, xlsx_text_en=None, txt_file_xlsx_it=file_path, txt_file_xlsx_en=None)
                        xlsx_new.save()
        
                serializer = XLSXSerializer(xlsx_new)

                return JsonResponse(serializer.data)   


            else:
                with self.lock:

                    with open(file_path, "wb") as out:

                        towrite = extraction(uploaded_file)
                        towrite = translate(towrite)
                        out.write(towrite.encode('utf-8'))

                with transaction.atomic():
                    xlsx_new = XLSX.objects.create(
                    title=file_path_xlsx, xlsx_file=uploaded_file, xlsx_text_it=None, xlsx_text_en=towrite, txt_file_xlsx_it=None, txt_file_xlsx_en=file_path)

                    xlsx_new.save()
        
                serializer = XLSXSerializer(xlsx_new)

                return JsonResponse(serializer.data)               

        else:
            if os.path.exists(file_path):  # il file .txt è già stato creato
                xlsx = XLSX.objects.filter(title=file_path_xlsx).first()
                serializer = XLSXSerializer(xlsx)
                return JsonResponse(serializer.data)
            else:
                if(language == 'it'):
                    with self.lock:
                        with open(file_path, "wb") as out:

                            towrite = extraction(uploaded_file)
                            out.write(towrite.encode('utf-8'))

                    # recupero record
                    queryset = XLSX.objects.select_for_update().filter(title=file_path_xlsx) .all()

                    with transaction.atomic():
                        queryset.update(xlsx_text_it = towrite, txt_file_xlsx_it = file_path)    
                    
                    xlsx = XLSX.objects.filter(title=file_path_xlsx).first()

                    #serializzazione
                    serializer = XLSXSerializer(xlsx)

                    # return jsonResponse
                    return JsonResponse(serializer.data)

                else:
                    with self.lock:
                        with open(file_path, "wb") as out:

                            towrite = extraction(uploaded_file)
                            towrite = translate(towrite)
                            out.write(towrite.encode('utf-8'))

                    # recupero record
                    queryset = XLSX.objects.select_for_update().filter(title=file_path_xlsx).all()

                    with transaction.atomic():
                        queryset.update(xlsx_text_en = towrite, txt_file_xlsx_en = file_path)

                    xlsx = XLSX.objects.filter(title=file_path_xlsx).first()

                    #serializzazione
                    serializer = XLSXSerializer(xlsx)

                    # return jsonResponse
                    return JsonResponse(serializer.data)
                 

