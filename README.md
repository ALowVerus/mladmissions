# Virtual Guidance Counselor
Created for HackDartmouthV (April 6th-7th 2019).

In the simplest terms, this is a chat bot that serves as a virtual guidance counselor in the college application process.

## Features
* Determine your chance of being accepted to specific schools
* Determine the likelihood of your acceptance to your entire portfolio of schools
* The scraped data is parsed into csv files having SAT, ACT scores along with GPA columns.
* Get recommendations based on your info and currently selected schools

## Data
* The data is processed using pandas to remove null values and the target column in transformed into binary values(i.e did the subject receive an acceptance or not). This makes our goal a Binary classification problem.
* Overall, the data seem to pose class imbalance problem.
* To handle the class imbalance we've employed [SMOTE](https://jair.org/index.php/jair/article/view/10302) technique 
* The data is analysed at different college level to predict better results.
* GPA and SAT scores tend to help us predict the target better here.
* Finally, classification methods - Gaussian Naive Bayes, Quadratic discriminant analysis and Random forest from sklearn are being used to classify our datasets.

## Tech
* Data was gathered by scraping our Naviance portals using accounts we had from high school
* Uses [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) to scrape Naviance
* Uses [Telegram](https://telegram.org/) for user interaction with the "guidance counselor." The bot itself is written in Python.
* [Python](https://www.python.org/) Programming language for developing ML algorithms.
* [Pandas](https://pandas.pydata.org/) library for data processing
* [sklearn](https://scikit-learn.org/stable/) library for training ML algorithms
* [imblearn](https://github.com/scikit-learn-contrib/imbalanced-learn) to perform oversampling
