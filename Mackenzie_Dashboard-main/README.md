# Mackenzie Monitoring Dashboard

## General Information

The Dashboard was created using Dash within Python.

Dash provides a set of python packages that allow creating an interactive website/dashboard using 'pure' Python code. The main components are:
* `dash_core_components` ...
* `dash_html_components` provide the same functionalities as html tags and are used to structure the page / create the layout
* `dash_bootstrap_components` provide a range of layout components (textboxes, buttons, navigation bar, etc.) and can be used to make the webpage responsive (adapt to the screen size)
* `callbacks` control all the interactive features

## File Structure

```
.
├── assets
│   ├── Pictures
|   │   ├── compressed
|   |   |   └── Compressed pictures for the Photo album 
|   |   └── Pictures for the Photo album
│   ├── style.css
│   ├── favicon.ico
│   ├── background1.png
│   ├── Logos (Dashboard, AWI, ...)
│   ├── Team photos
│   └── ...
├── data
│   ├── Duccem data
│   ├── Mackenzie Arctic GRO discharge
│   ├── Parameter_Info.csv
│   └── ...
├── multipage_app.py
├── index.py
├── layouts.py
├── callbacks.py
├── requirements.txt
├── runtime.txt
└── Procfile

```

The folder may currently contain additional files that are not used or deprecated.

## File content



* `multipage_app.py` initializes a Dash class (this file doesn't need to be changed when changing the website)
* `index.py` must be executed in order to run the website locally
* `layouts.py` contains the layout of each page (in this case two: home and contact page)
* `callbacks.py` holds all figures and the interctive functionalities of the page. E.g. show the parameters from the dropdown in the plots, show next image in slideshow, when the arrow is clicked etc.
* `requirements.txt` is a list of all python packages needed. Before working on the page locally, the command `pip install requirements.txt` can be executed to ensure, that the local environment holds all packages.
* `runtime.txt` contains the python version that should be used (relevant for Heroku to be able to host the page correctly)
* `Procfile` contains information on the server that should be used (relevant for Heroku)

## Useful Ressources

* [RealPython](https://realpython.com/python-dash/) step by step guide to create a Dash app from the scratch
* [Dash Plotly documentation page](https://dash.plotly.com/)
* [Bootstrap documentation page](https://dash-bootstrap-components.opensource.faculty.ai/)
* YouTube channel [Charming Data](https://www.youtube.com/c/CharmingData) focussing on Dash
