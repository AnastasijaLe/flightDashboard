# Django Flight Dashboard

## Projektu veidoja
Raivo

Renārs

Anastasija

## Apraksts

Programmatūra vizualizē datus izmantojot vairākas bibliotēkas. Programmatūra sniedz iespēju izvēlēties vienu no septiņām kategorijām, lai veicinātu vēlamo datu atrašanu.
[The Navigation section of flight dashboard, containing 7 choices - Overview, Flights, Passengers, Aircraft, Crew, Financial and Weather,](https://cdn.discordapp.com/attachments/1159108472076513323/1435249553321230336/image.png?ex=690b47cf&is=6909f64f&hm=7364280c2ee4af46848d10e9e6f6d15aae4ff171e3a66f9073e33bc5437d6718&)

![The overview tab of the dashboard, containing a piechart regarding flight status, and a bar chart regarding flight count](https://media.discordapp.net/attachments/1159108472076513323/1435248258825064448/image.png?ex=690b469a&is=6909f51a&hm=996e2e50deef2cdf0a9c7182aef29b60d0f54c24e253ec2dd5c30b731618507f&=&format=webp&quality=lossless)

Dažās kategorijās ir papildus interaktivitāte - iespējams sašaurināt vēlamo datu loku sīkāk.
![An interactive calendar with an option to choose a date](https://media.discordapp.net/attachments/1159108472076513323/1435248430778810509/image.png?ex=690b46c3&is=6909f543&hm=4c331da1ec6d1ef80ccc95ccc5f11610b9fe2c5e54bef946517db73b43ff0f59&=&format=webp&quality=lossless)

## Arhitektūra
Flight Dashboard balstās uz datubāzes, kuru var rediģēt izmantojot django, vizuālie elementi tiek apstrādāti ar streamlit un citām python bibliotēkām.
![alt](https://media.discordapp.net/attachments/1427226047841308682/1429808958587142205/myapp.png?ex=690b435c&is=6909f1dc&hm=246fb6679970307842523c106b19b2520ab2df419205472e5fb083d6fed03474&=&format=webp&quality=lossless&width=1620&height=836)

## Uzlabojumi nākotnei
- reālu datu izmantošana
- papildus kategorijas


## Izmantotās bibliotēkas
streamlit
pandas
django
django-extensions
python-dateutil
pytz
plotly
## Sākuma soļi
### Darot secībā
```bash
git clone https://github.com/AnastasijaLe/flightDashboard.git
cd flightDashboard
python -m venv venv
```
### Uz Linux/bash
```bash
source venv/bin/activate
```
### Windows
```
venv\bin\activate
```
### Dependancies un darbināt serveri
```bash
pip install -r requirements.txt
python manage.py runserver
```

## Datubāzes pārģenerācija

```
python populate.py
```
## UML Generator

```
pip install django-extensions
```
## Ja pygraphviz vai pydorplus ir ielādēts

```
python manage.py graph_models -a -o myapp_models.png
```

## Bet ja nav, vajag izveidot dot failu un pārveidot to

```
python manage.py graph_models -a --dot -o myapp_models.dot
dot -Tpng myapp_models.dot -omyapp_models.png
```

## Kā darbināt Streamlit frontend

```
python -m streamlit run app.py
```


