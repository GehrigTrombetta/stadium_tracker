# IST 356 Final Project: Stadium Finder

Student Name(s): Gehrig Trombetta

### What the code does and results

This is an interactive Streamlit app that finds the closest sports venues to a selected team or a user-provided address. The user can search by picking a team from the NBA, NFL, MLB, NHL, MLS, or WNBA, or by entering a street address. The app calculates distances using the Haversine formula and displays results in a sorted dataframe and an OpenStreetMap-based interactive map with color-coded markers per league. Users can control how many teams per league are shown and filter which leagues appear in the results.

### How to run the code

1.  In the terminal, activate your `ist356` conda environment:

    ```bash
    conda activate ist356
    ```
    
    You should see the text to the left of the prompt change to `(ist356)`.

1. Now install the required packages by running:

```bash
   pip install -e .
```
and
```bash
   pip install -r requirements.txt
```

2. From the project root, run:

```bash
   streamlit run finalproject/stadiumfinder.py
```

3. The app will open in your browser. Select **Team** or **Address** mode, configure your options, and click **Find closest stadiums**.

#### Unit tests

Tests are located in `tests/test_package.py` and cover the core utility functions: distance calculation, location formatting, emoji helpers, and the Google geocoding API (using mocked HTTP responses).

To run the tests, from the project root:

```bash
python -m pytest tests
```