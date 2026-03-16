-- development handled by: Thineth Weerasinghe --

Est_Handler - main module for data extraction and estimation. identifies which type of input it is and proceeds to required module.
Label_Extraction - used to extract the nessecery information from the Raw OCR data provided if it is a scanned label.
Estimation_Search - searches the database for the current food item and provides the foods nutritional estimation based on name and quantity.
Logger - logs data into log file with time and info


-- Estimation_Search
the estimation handles inputs of (item name, quantity)
it runs the provided name through a set of different datasets individually in the provided order:
1. frequented_foods.csv
2. NutriScannerDB.csv (maybe skip this one)
3. IRD.csv
4. Fastfood.csv
5. External files
6. USDA.csv

frequented_foods.csv contains a dataset unique to each individual user, after each use of the application by the user the food item they scanned will be appended to it. it stores the 50 most recent food items the user has searched. this allows for a faster search as users are likely to repeat food items native to their diet
NutriScannerDB.csv contains data maintained by the team at nutriscanner it contains global statistics of the most scanned foods along with a tally of how many times they have been scanned determining the ranking of foods, this allows for fast searches as there are multiple common food items in the majorities diet such as white bread.
datasets 3-5 are standard and will be searched if 1 and 2 do not provide results.
in the case that none of them provide results the USDA dataset is checked. it is a robust dataset containing most food items, however it is checked last as it is extrememly large.

In the scenario that the food item was not found it checks the ontologies for similar names to the food provided and runs the search again from frequented_foods.csv.
If this does not produce a result return a not found error.