[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![version](https://img.shields.io/badge/version-3.0-blue)](https://github.com/sak007/IOT-HW4/releases/tag/v3.0)
[![DOI]()]
[![GitHub issues](https://img.shields.io/github/issues/sak007/IOT-HW4)](https://github.com/sak007/IOT-HW4/issues?q=is%3Aopen+is%3Aissue)
[![GitHub closed issues](https://img.shields.io/github/issues-closed/sak007/IOT-HW4)](https://github.com/sak007/IOT-HW4/issues?q=is%3Aissue+is%3Aclosed)
[![Github pull requests](https://img.shields.io/github/issues-pr/sak007/IOT-HW4)](https://github.com/sak007/IOT-HW4/pulls)
[![Github closed pull requests](https://img.shields.io/github/issues-pr-closed/sak007/IOT-HW4)](https://github.com/sak007/IOT-HW4/pulls?q=is%3Apr+is%3Aclosed)

# Content

| S.No | Title | Hyperlink |
|-|-|-|
|1.|Background|[click here](#background)|
|2.|Setup Instructions|[click here](#setup-instructions)|

# Background

## Machine Learning Code
Found in code/ML

Data2.ipynb - Python notebook for processing the training data for the machine learning model

Model2.ipynb - Python notebook for creating the machine learning model, after training is complete, a folder called models is created, containing the checkpoint model for each epoch, the best epoch is selected and copy and pasted to code/ML/myModel, renaming the checkpoint folder name to myModel, additionally, it is to be copied to /code/classifier/myModel

myModel directory - the saved machine learning model

predict.py - python script to load the machine learning model and make predictions on data

pretty.py - used to generate confusion matrix for model training

## Classifier

Classifier should be executed in a server so that it can receive the data from the Raspberry Pi attached in the door and run the classification algorithm. The result from the classifier is then sent to the monitor device.

## Raspberry Pi in the door

The role of the Raspberry Pi attanched in the door is to send the data stream to the classifier whenever an even occurs (whenever a movement is detected).

## Monitor

This device receives information from the classifier and displays the state of the door in the terminal.


# Setup Instructions

## Classifier
  - run ```pip3 install -r requirements.txt``` from the project root directory.
  - Update appId, key and token in ```application.yaml``` inside **code/classifier** directory.
  - run ```python3 subscriber.py``` from **code/classifier** directory to start the model.
  
## Raspberry Pi in the door
  - Enable I2C in the RaspberryPi.
  - Set I2C speed to 400KHz ([Click here for instructions](https://www.raspberrypi-spy.co.uk/2018/02/change-raspberry-pi-i2c-bus-speed/))
  - run ```pip3 install -r requirements.txt``` from the project root directory.
  - Update orgId, typeId, deviceId and token in ```device.yaml``` inside **code/door** directory.
  - run ```python doorEventDetect.py``` from **code/door** directory.

## Monitor
  - run ```pip3 install -r requirements.txt``` from the project root directory.
  - Update orgId, typeId, deviceId and token in ```device.yaml``` inside **code/monitor** directory.
  - run ```python3 wiotpClient.py``` from **code/monitor** for displaying the door status in the terminal.



