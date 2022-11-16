# Resplanning Back

## Introduction

This is the back app of resplanning. Resplanning is a tool to generate a planning depending on constraints.

Constraints are decomposed in three parts :
* Rules by slot
* Rules by person 
* Availability

Due to an optimization problem, constraints by slot are limited (~ at most 15 people on 20).
You can try to improve this app, but please respect the license.

## Setup

### Installation 

Create a python environnement if you want then :

`pip install -r requirements`

Then you need to fill `settings.py`

### Run 

You just need to run this command :

`uvicorn main:app --reload`

## License

Shield: [![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg
