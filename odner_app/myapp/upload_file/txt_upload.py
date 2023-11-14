import os
import re
import logging
import getpass
from django.http import JsonResponse
from rest_framework import generics
from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator

from myapp.models import PDF
from myapp.serializers.pdf_serializer import PDFSerializer
import threading
from django.db import transaction


class TXTUploadView(generics.CreateAPIView):

    """
    View for uploading a TXT file and saving its extracted and translated text.
    """

    lock = threading.RLock()

    def extraction(to_extract):
        """
        Extract text from the given PDF and clean it up.
        
        :param to_extract: path to the PDF file
        :return: cleaned text as a string
        """
        pdf = PdfReader(to_extract)

        towrite = ""

        for page in pdf.pages:
            text = page.extract_text()

            for line in text:
                if(line == '\n') | (line == '\r') | (line == '\r'):
                    towrite = towrite + ' '
                else:
                    towrite = towrite + line

        pattern = r'(\w)-\s*(\w)'
        pattern2 = r'(\w)-\n*(\w)'
        pattern3 = r'(\w)-\n\s*(\w)'
        replacement = r'\1\2'
        towrite = re.sub(pattern, replacement, towrite)

        towrite = re.sub(pattern2, replacement, towrite)

        towrite = re.sub(pattern3, replacement, towrite)

        towrite = re.sub(' +', ' ', towrite)

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

    def post(self, request, *args, **kwargs):
        """
        Process the uploaded PDF file and save its extracted and translated text.
        
        :param request: HTTP request.
        :type request: HttpRequest.
        :return: HTTP response.
        :rtype: JsonResponse.
        """
        logger = logging.getLogger('appLog')
        uploaded_file = request.FILES.get('file', None)
        logger.error("START")
        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'})
        
        language = request.data.get('language', None)

        file_name = uploaded_file.name

        txt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'txt_files/txt/')

        if not os.path.exists(txt_dir):
            os.makedirs(txt_dir)
        logger.error("txt_dir")

        logger.error(txt_dir)
        #txt_dir = '/tmp/'
        file_path = os.path.join(txt_dir, file_name[:-4]+'-' + language + '.txt')
        
        file_path = re.sub("/C%3A","C:",file_path)

        logger.error(os.getcwd())
        logger.error("file_path")

        logger.error(file_path)

        file_path_pdf = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'myapp_file/pdfs/', file_name)
        logger.error("filepathpdf")

        logger.error(file_path_pdf)

#        file_path_pdf=os.path.basename(file_path_pdf)

        logger.error('uploadfile')
        #file_path_pdf = '/tmp/'+file_name
        logger.error(uploaded_file)
        logger.error(language) 
        pdf_new = None
        logger.error(os.path.exists(file_path_pdf))
        if not(os.path.exists(file_path_pdf)):
            if(language == 'it'): #estrazione in italiano
                

                with self.lock:
                    with open(file_path, "wb+") as out:
                        #towrite = uploaded_file #towrite = PDFUploadView.extraction(uploaded_file)
                        towrite = str(uploaded_file.read())

                        out.write(towrite)

                pdf_new = PDF.objects.filter(title = file_path_pdf).first()
                logger.error(pdf_new)
                logger.error(file_path)
                logger.error(file_path_pdf)
                if pdf_new:
                    queryset = PDF.objects.select_for_update().filter(title = file_path_pdf).all()
                    with transaction.atomic():
                        queryset.update(title=file_path_pdf, pdf_file=uploaded_file, pdf_text_it=towrite, pdf_text_en=None, txt_file_pdf_it=file_path, txt_file_pdf_en=None)
                else:

                    with transaction.atomic():
                        pdf_new = PDF.objects.create(title=file_path_pdf, pdf_file=uploaded_file, pdf_text_it=towrite, pdf_text_en=None, txt_file_pdf_it=file_path, txt_file_pdf_en=None)
                        #pdf_new = PDF.objects.create(title=file_path_pdf, pdf_file=uploaded_file)

                        pdf_new.save()
        
                serializer = PDFSerializer(pdf_new)

                return JsonResponse(serializer.data)
        
            else:
                with self.lock:
                    with open(file_path, "wb+") as out:

                        towrite = (uploaded_file.read())
                        #logger.error(towrite)
                        out.write(towrite)
                logger.error("Here2")
                logger.error(type(towrite))
                string =  towrite.decode('utf-8')
                logger.error(string)
                if pdf_new:
                    queryset = PDF.objects.select_for_update().filter(title=file_path_pdf).all()

                    with transaction.atomic():
                        queryset.update(
                            title=file_path_pdf, pdf_file=uploaded_file, pdf_text_it=None, pdf_text_en=string, txt_file_pdf_it=None, txt_file_pdf_en=file_path)

                else:

                    with transaction.atomic():
                        pdf_new = PDF.objects.create(
                            title=file_path_pdf, pdf_file=uploaded_file, pdf_text_it=None, pdf_text_en=string, txt_file_pdf_it=None, txt_file_pdf_en=file_path)
                        pdf_new.save()

                serializer = PDFSerializer(pdf_new)

                return JsonResponse(serializer.data)
        else:
            if os.path.exists(file_path):
                # il file .txt è già stato creato
                pdf = PDF.objects.filter(title=file_path_pdf).first()               
                towrite = uploaded_file.read()
                string =  towrite.decode('utf-8')
                logger.error(string)
                queryset = PDF.objects.select_for_update().filter(title=file_path_pdf).all()

                with transaction.atomic():
                        queryset.update(pdf_text_en = string[5:], txt_file_pdf_en = file_path)

                pdf = PDF.objects.filter(title=file_path_pdf).first()
                pdf.save
                serializer = PDFSerializer(pdf)
                #serializer = PDFSerializer(queryset)
                logger.error("here3")
                return JsonResponse(serializer.data)
            else:
                if(language == 'it'):
                    
                    with self.lock:
                        with open(file_path, "wb") as out:

                            towrite = uploaded_file #towrite = PDFUploadView.extraction(uploaded_file)
                            out.write(towrite.encode('utf-8'))
                    string =  towrite.decode('utf-8')
                
                    # recupero record

                    queryset = PDF.objects.select_for_update().filter(title=file_path_pdf).all()

                    with transaction.atomic():
                        queryset.update(pdf_text_it = towrite, txt_file_pdf_it = file_path)   
                    
                    pdf = PDF.objects.filter(title=file_path_pdf).first()
                    
                    #serializzazione
                    serializer = PDFSerializer(pdf)

                    # return jsonResponse
                    return JsonResponse(serializer.data)

                else:
                    
                    with self.lock:
                        with open(file_path, "wb") as out:
                            towrite = uploaded_file.read()
                            #towrite = PDFUploadView.translate(towrite)
                            out.write(towrite)
                            logger.error(towrite)
                    
                    # recupero record
                    queryset = PDF.objects.select_for_update().filter(title=file_path_pdf).all()
                    string =  towrite.decode('utf-8')

                    with transaction.atomic():
                        queryset.update(pdf_text_en = string, txt_file_pdf_en = file_path)
                    
                    pdf = PDF.objects.filter(title=file_path_pdf).first()
                    pdf.save
                    #serializzazione
                    serializer = PDFSerializer(pdf)
                    logger.error("here")
                    # return jsonResponse
                    return JsonResponse(serializer.data)
