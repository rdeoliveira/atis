## Introduction

**All** instructions below assume you are in the root directory `atis` and virtual environment explained in the **App/Set-up** section.

This package contains:
* An **application** to predict intents and slots from utterances about flight booking.
* Data and scripts to re-train the **model** used in the app.
* **Documents** explaining the training and performance of the model.

## Requirements
* A bash terminal
* [Python 3.6.5](https://www.python.org/downloads/). Apologies for a very specific version of Python, but some dependencies had issues (e.g. ONNX) with other versions (e.g. 3.7).
* [virtualenv](https://virtualenv.pypa.io/en/latest/installation/)

## App

### Set-up
Create and activate a virtual environment, then install dependencies in the environment:
```
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### Usage
Start the server and supply queries from command line:
```
$ export FLASK_APP=app.py
$ flask run
(in new terminal window/tab, navigate to root dir again and activate the same venv)
$ function query() { curl http://localhost:5000/get_flight_info -H "Content-Type: text/plain" -d "$1"; }
$ query 'what is the cheapest flight going to new york city on march 24th in the morning'
```

If all went well, you'll see:
```
{
  "intent": "flight", 
  "slots": "{'cost_relative': 'cheapest', 'toloc.city_name': 'new york city', 'depart_date.month_name': 'march 24th', 'depart_time.period_of_day': 'morning'}"
}
```

Try other queries and have fun!

### Tests
```
$ python3 test_app.py
```

If all went all, you'll see something like:
```
WARNING:root:This caffe2 python run does not have GPU support. Will run in CPU only mode.

query: show me flights from miami to new york
response: {
 "intent": "flight",
 "slots": {
  "fromloc.city_name": "miami",
  "toloc.city_name": "new york"
 }
}
.
query: 
response: {
 "error": "No query supplied."
}
.
query: me mostre voos de miami para nova iorque
response: {
 "intent": "distance",
 "slots": {
  "city_name": "miami"
 }
}
.
query: make me a cup of coffee
response: {
 "intent": "restriction",
 "slots": {}
}
.
query: !@£$%^&*()_+-=\{\}[]:";'<>?,./~`
response: {
 "intent": "flight",
 "slots": {}
}
.
----------------------------------------------------------------------
Ran 5 tests in 0.068s

OK
```

## Model

### Preparation
Prepare the supplied raw data so that PyText can use it:
```
$ python3 data/data_processor.py --download-folder data/raw --output-directory data
```

You should see:
```
Train/Validation data written successfully at  data/atis.processed.train.csv and data/atis.processed.val.csv
Test data written successfully at  data/atis.processed.test.csv
```

Download and unzip pre-trained word embeddings (c. 860 Mb or 5 min), to increase the model's performance:
```
$ curl https://nlp.stanford.edu/data/wordvecs/glove.6B.zip > data/glove.6B.zip
$ unzip data/glove.6B.zip -d data
```

### Training
Train the model as per configuration file (c. 20 min):

```
$ pytext train < atis_config.json
```

If all went all, you should see the following files in `./output`:
* `atis_model.c2`: the model in Caffe2 format.	
* `atis_model.pt`: the model in PyTorch format.
* `atis_model.onnx`: the model in ONNX format.
* `test_out.txt`: the test results.

`test_out.txt` is a tab-delimited file with following 4 headers: `doc_index`, `text`, `predicted_annotation`, `actual_annotation`. If you want to convert it to a csv file with headers `text`, `golden intent/slots`, `predicted intent/slots`: 
```
$ python text2csv.py output/test_out.txt output/test_out.csv
```
## Documents

### Report
The file `docs/report.pdf` describes the training of the model in more detail.

### Scores
The above training should have displayed performance scores on console. If you want to store them in a file:
```
$ pytext test < atis_config.json > docs/scores.txt
```

The file `docs/scores.txt` should contain scores similar to:
```
Intent Metrics
	Per label scores                        	Precision 	Recall    	F1        	Support   

	flight                                  	98.26     	98.58     	98.42     	632       
	...        

	Overall micro scores                    	97.09     	97.09     	97.09     	893       
	Overall macro scores                    	70.08     	74.43     	70.64     


Slot Metrics
	Per label scores                        	Precision 	Recall    	F1        	Support   

	toloc.city_name                         	97.26     	99.44     	98.34     	715       
	...        

	Overall micro scores                    	95.45     	95.62     	95.53     	2260      
	Overall macro scores                    	70.02     	72.69     	70.38     
```