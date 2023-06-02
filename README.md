# envirnonment setup NECESSARIO PYTHON v. 3.9.13 O SUPERIORE

## all'interno della cartella odner_app/

```

python -m pip install --upgrade pip

pip install virtualenv  

virtualenv venv

source venv/bin/activate  # Activate the virtual environment (Linux/Mac)

myenv\Scripts\activate     # Activate the virtual environment (Windows)

pip install -r requirements.txt

python -m spacy download en_core_web_trf

python -m spacy download it_core_news_lg

```


# frontend - on localhost (development server)

## All'interno della cartella "frontend" in una finestra del terminale


### Compiles and hot-reloads for development
```
npm run serve
```

# backend - on localhost (development server)

## all'interno della cartella dove si trova il file "manage.py" IN UNA NUOVA FINESTRA DEL TERMINALE ALL'INTERNO DELLA CARTELLA odner_app/

### Start server posizionato all'interno della cartella dove si trova il file "manage.py"
```
python.exe ./manage.py runserver
```

# cancellare record del database (reset delle info salvate) - cartella odner_app/
```
python.exe ./delete_record.py
```

