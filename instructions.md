# Instructions

For this project you can do anything you want, provided it uses what we learned in the course. Here's a summary of what's expected:

1. Python functions in modules with tests

2. Either a Streamlit app or a set of command-line executables (that use argparse) for user interface.

3. Pandas for data manipulation

4. Visualizations

5. APIs (cent.ischool-iot.net portal or any other API's of your choosing) and/or  
Web Scraping using playwright if you cannot find an API.


## Turning it in

As with the homework assignments, you will turn in the project by commiting and pushing changes to this repository. The repository has:

- `README.md`: this is where you will put your written report about the project.
- `finalproject` folder: put your codes here
- `tests` folder: put your unit tests here
- `pyproject.toml`: a toml file that lets you install your code into your conda environment
- `requirements.txt`: a list of packages that need to be installed in order for your code to run
- `reflection.md`: your reflection
- `instructions.md`: this file

To get full credit, your final repository should have the following:

1. A `finalproject` folder that contains all of your code. Your code should involve at least a couple of functions you write.

1. A `tests` folder that contains your unit tests for any functions that you've written in your code.

1. A README.md file that explains what the code does and shows any results you have (these can be in the form of plots). If you write a Streamlit app, the README should have instructions on how to use the app. In either case, I should be able to follow the instructions in your README to reproduce your results using the code in the `finalproject` folder, and run the tests in the `tests` folder. If you need to install any additional packages for your code to work, you need to put them in `requirements.txt`. I will deduct
points if I cannot successfully run your code simply by following your README.md.

1. A well written reflection.md

## Installing & importing code

I have provided a pyproject.toml file for you. As with the assignments, you can install code that you write in the `finalproject` directory by doing the following:

1.  Open a terminal. Make sure you are in your final project directory by typing `pwd`. If not, `cd` to where every you cloned the repository to on your computer.

1.  If it is not already activated, activate your `ist356` conda environment by running:

    ```{bash}
    conda activate ist356
    ```

1.  Now install your finalproject code by running:

    ```{bash}
    pip install -e .
    ```

Any code you write in the `finalproject` folder can then be imported and used in other code and by tests in your test directory. For example, suppose you create a module in the `finalproject` directory called `mymod.py`, and in `mymod.py` you write a function called `foo`:

```{python}
# mymod.py
def foo():
    # ... do something
    return # something
```

You can import this into another script (say, a Streamlit app or command-line executable also in `finalproject`, or test function in `tests`) `finalproject` directory by running:

```{python}
from finalproject import mymod

# Now use the foo function somewhere in your code with...
mymod.foo()
```


## Grading

The project is worth 24 points in total. You will be graded on:

- A well-written, clear README.md file that illustrates your results and explains how to use your code. (6 points)
- Working code that I can run to reproduce your results (6 points)
- Unit tests of your functions with sensible tests that pass (6 points)
- A well written reflection (6 points)

## What Type of Project Should I Do?

Its up to you! Do you need some ideas? Consider building a data pipeline like we did in assignment 04/05/06 and then building a dashboard around the data using visualizations and streamlit.

Break your pipeline up into separate python programs to perform each step similar to assignment 05 and 06.


1. Extract data from API's / web scraping / or a dataset. Save the data to a file in your cache folder.

2. Transform the data into a format that is useful for your dashboard. Save the data to a file in your cache folder.

3. Load the data into a pandas and interact with it using streamlit and charts, graphs or maps.

4. part of your extract or transform steps you might need to write functions. Make sure you write tests for these functions, similar to what has been demonstrated in the class assignments.


## I need more inspiration...

Here's a place where you can find API's that might interest you:

- Awesome Public API's: https://github.com/public-apis/public-apis
- US Government API's: https://api.data.gov/
- Portal of Public APIs: https://publicapis.dev/
- Always welcome to use: https://cent.ischool-iot.net/


Here's a suggestion for data sources / datasets of interest:

- SU Library: https://researchguides.library.syr.edu/az/databases?t=8828
- Data Catalog: https://data.world/datasets/free
- Most cities have an open data portal, for example: https://opendata.cityofnewyork.us/
- British Film Institute: https://www.bfi.org.uk/industry-data-insights
- NASA Data, for example: https://www.earthdata.nasa.gov/
- Sports Data: https://www.sports-reference.com/
- US Government data: https://data.gov/
- Google Dataset Search: https://datasetsearch.research.google.com/
- Kaggle Datasets: https://www.kaggle.com/datasets
- Awesome Public Datasets: https://github.com/smuthubabu/awesome-public-datasets


## In summary

It is important to me that I see "YOU" in your project. That means:

- Share what you learned,
- Do something that interests you,
- Explain what you did and how it works!
