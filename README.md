
## Survey Data Extraction and Analysis

## Description

This project extracts information from a survey report file (in PDF format) and processes it using natural language processing (NLP) techniques to extract valuable insights. The code is divided into three parts: PDF Reading, Filtering and Preprocessing, and NLP and Data Exploration.

This tool for extraction of the data from both structured and unstructured data source which could be in text, image, or any other formats.
Particyularly, our field of interest is Corrosion related data.


## Libraries Used

The following libraries are used in the code:

- PDF_Reading
- Filtering_and_preprocessing
- NLP_and_data_exploration
- pickle
- os, etc.

Install Python IDE (Recommendation anaconda(package) which has Jupyter notebooks and Spyder for Python) and following python packages
a.	Pdfminer
b.	Io
c.	Camelot – See the description to install this package (needs ghostscript and tkinter)  https://pypi.org/project/camelot-py/
d.	difflib
e.	numpy
f.	re
g.	nltk
h.	dateutil
i.	pandas

## Input Data

The input data required for the code is a PDF file location. The user needs to specify the location of the PDF file, which will be used as input for the code. The input file should contain relevant information that needs to be extracted and analyzed.

# other data like "parts and sub-parts name whose associated data will be searched for can be given manually under ‘manually_feeding_location_name’.
and under ‘sub_parts_string_list’
(Note: if not above data provided the tool will attempt to detect the location name available in the pdf file under the tables with column title ‘location’)

## Usage

- First, provide the file location of the PDF file.
- The code then checks if the extracted pickle file exists. If it doesn't exist, the code extracts the text from the PDF and stores it in a segmented pages pickle file.
- Next, the code filters and preprocesses the segmented pages using the `filtering_and_preprocessing_pages` function.
- The code then extracts the location information from the filtered and preprocessed pages using the `extract_all_elements_from_columns_related_to_key_word` function.
- The code extracts information from the text part of the pages using the `get_list_of_information_explorer_from_text_in_segmented_pages` function.
- The code extracts information from the tables in the pages using the `extract_informations_from_tables` function.
- The code then exports the extracted information from the tables and text as CSV files in a specified folder.

## Output Data

The code outputs the following:
- The extracted pages are saved in ‘pickle’ format which saves time allowing us to read from it, instead of reading the pdf page again in case needed further.
- `*_information_from_text.csv`: CSV file containing extracted information from the text part of the PDF file.
- `*_tables_extracted.csv`: CSV file containing extracted information from the tables in the PDF file.
- `*_tables`: Folder containing individual CSV files of each table in the PDF file.

## Author

- Name: Madhu Sudan Sapkota


