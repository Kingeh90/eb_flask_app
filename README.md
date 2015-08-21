Fun mobile app
==========

## Create and activate the virtualenv
    virtualenv -p python2.7 /tmp/eb_flask_app
    . /tmp/eb_flask_app/bin/activate

## Install dependencies
Cd into the `eb_flask_app` dir and install the requirements:
    
    cd eb_flask_app
    pip install -r requirements.txt
    
## Factual credentials
Register at `https://www.factual.com/` and generate a factual key and secret. These have to go in the
`factual_credentials.py` and the file has to exist in the `eb_flask_app` folder. My `eb_flask_app` looks like this:

    ├── application.py
    ├── factual_credentials.py
    ├── __init__.py
    ├── middleware.py
    ├── mocks
    │   ├── __init__.py
    │   └── mocks0.json
    ├── README.md
    ├── README.pdf
    ├── requirements.txt
    ├── tests.py
    └── utils.py

My `factual_credentials.py` looks like this:
    
    key = 'r5xZGg9R5farar3494hna239OCMN0afdfRzafdt' (not real) 
    secret = 'camL0STfp6CfaffafdsafafasfDEMZ3RWKAfnh5y' (not real)


## Run application

    python application.py
    
This message should appear:

     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat

Go to http://127.0.0.1:5000/ to access the status page.

## How to use the api

There are three endpoints exposed for the application.

#### @app.route('/')
This endpoint checks for the server status and version string.
On your browser go to http://127.0.0.1:5000/

You should get the following on your browser with the current timestamp:
    
    {"status": "live", "author": "Sudipta Basak",
    "version": "0.1.0", "datetime": "2015-08-17T01:17:36.303770"}

Or one could use
    
    curl http://127.0.0.1:5000/

#### @app.route('/task1/\<location\>/\<search_string\>')

On this endponint, given an Australian location and	a place	of interest, returns a list of 5 recommendations. 
Suggestions	may	be type	of restaurant or drink,	like “indian”, “coffee”. The locations are returned	in order of	
nearest	to	furthest. 

Either use 
    
    curl http://127.0.0.1:5000/task1/epping/coffee
   
or use a rest api client like postman to view this output.

This endpoint, as the name suggests, addresses the task1. The inputs `location` and `search_string` have be to of the
following form:

    1. location: Australian place or postcode.
    2. search string: examples include 'coffee', 'thai', 'indian'.

The best location is decided based on two different strategies depending on the situation.
If a factual database filter returns multiple matches, then the location is chosen based on the device ip. The location
closest to the device ip is chosen as the location. Otherwise, if no direct match is found in the database,
a likelihood search on the factual database decides the location.
The top of the list returned by factual database search is chosen in this case.

Location names can contain spelling mistakes, or approximate names, and may be picked up by the api.

#### @app.route('/task2/\<location\>/\<meal_of_the_day\>', methods=['POST'])
This end point accepts a group of co-workers and their likes, dislikes and dietary requirements, uses the Factual API
to produce a list of 5 recommendations for the best location. Essentially what we have is matching a common location
to a list of likes and dislikes taking into account any special dietary requirements. 

The inputs has be to of this form:

    1. location: Australian place or postcode.
    2. meal_of_the_day: one of 'breakfast', 'lunch', or 'dinner'.

The meal of the day is a strict criteria as if the restaurant is not even it does not make sense to go there.
In the following example we see people have listed their favorite types of cuisine, 
their least favorites and dietary requirements (gluten free, vegetarian):

    [
        {
            "name":	"Bob",
            "title":	"executive",
            "likes":	[
                            "indian",
                            "chinese",
                            "malaysian"
            ],
            "dislikes":	["Australian"],
            "requirements": "gluten free"
        },
        {
            "name":	"Jose",
            "title":	"developer",
            "likes":	[
                            "indian",
                            "chinese"
            ],
            "dislikes":	["thai"]
        },
        {
            "name":	"Aloysia",
            "title":	"evangelist",
            "likes":	[
                            "chinese",
            ],
            "dislikes":	["Australian"],
            "requirements": "vegetarian"
    
        }
    ]

`requirements` string can be (close to) one of the following in Factual restaurant schema:

    vegetarian						
    vegan						
    glutenfree						
    lowfat						
    organic						
    healthy

I have used `difflib` to choose one of the above strings that matches closely. If no match is found, that requirement
will not be used. So one can provide `glutenfree` or `fluten fre` and still will get results for `glutenfree`.

Use postman, or curl to view this output.

A typical curl for `epping` and `lunch` would be:
    
    curl -H "Content-Type: application/json" -X POST -d '[{
        "name":	"Bob",
        "title":	"executive",
        "likes":	[
                        "indian",
                        "chinese",
                        "malaysian"
        ],
        "dislikes":	["Australian"],
        "requirements": "gluten free"},
    {
        "name":	"Jose",
        "title":	"developer",
        "likes":	[
                        "indian",
                        "chinese"
        ],
        "dislikes":	["thai"]},
    {
        "name":	"Aloysia",
        "title":	"evangelist",
        "likes":	[
                        "malaysian"
        ],
        "dislikes":	["Australian"],
        "requirements": "vegetarian"}]' http://127.0.0.1:5000/task2/epping/lunch

