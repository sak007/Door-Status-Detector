[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![version](https://img.shields.io/badge/version-3.0-blue)](https://github.com/sak007/IOT-HW4/releases/tag/v3.0)
[![DOI]()]
[![GitHub issues](https://img.shields.io/github/issues/sak007/IOT-HW4)](https://github.com/sak007/IOT-HW4/issues?q=is%3Aopen+is%3Aissue)
[![GitHub closed issues](https://img.shields.io/github/issues-closed/sak007/IOT-HW4)](https://github.com/sak007/IOT-HW4/issues?q=is%3Aissue+is%3Aclosed)
[![Github pull requests](https://img.shields.io/github/issues-pr/sak007/IOT-HW4)](https://github.com/sak007/IOT-HW4/pulls)
[![Github closed pull requests](https://img.shields.io/github/issues-pr-closed/sak007/IOT-HW4)](https://github.com/sak007/IOT-HW4/pulls?q=is%3Apr+is%3Aclosed)

# Boosting Raspberry Pi I2c speed
Make sure to set I2C speed to 400KHz
https://www.raspberrypi-spy.co.uk/2018/02/change-raspberry-pi-i2c-bus-speed/

# Machine Learning Code
Found in code/ML
Data2.ipynb - Python notebook for processing the training data for the machine learning model
Model2.ipynb - Python notebook for creating the machine learning model, after training is complete, a folder called models is created, containing the checkpoint model for each epoch, the best epoch is selected and copy and pasted to code/ML/myModel, renaming the checkpoint folder name to myModel, additionally, it is to be copied to /code/classifier/myModel
myModel directory - the saved machine learning model
predict.py - python script to load the machine learning model and make predictions on data
pretty.py - used to generate confusion matrix for model training

