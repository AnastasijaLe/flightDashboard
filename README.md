# Django Flight Dashboard

Sākuma soļi

```
git clone https://github.com/AnastasijaLe/flightDashboard.git
cd flightDashboard
python -m venv venv
source venv/bin/activate (Linux bash/bash deratives)
venv\bin\activate (Windows)
pip install -r requirements.txt
python manage.py runserver
```
Datubāzes pārģenerācija

```
python populate.py
```
UML Generator

```
pip install django-extensions
```
Ja pygraphviz vai pydorplus ir ielādēts

```
python manage.py graph_models -a -o myapp_models.png
```

Bet ja nav, vajag izveidot dot failu un pārveidot to

```
python manage.py graph_models -a --dot -o myapp_models.dot
dot -Tpng myapp_models.dot -omyapp_models.png
```

Kā darbināt Streamlit frontend

```
python -m streamlit run app.py
```
