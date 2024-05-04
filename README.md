![Logo](https://gi) 

<div align="center"> <h3> <a href="https://github.com/Solrikk/DataDresser/blob/main/README.md">English</a> | <a href="https://github.com/Solrikk/DataDresser/blob/main/README_RU.md">Russian</a> | <a href="https://github.com/Solrikk/DataDresser/blob/main/README_GE.md">German</a> | <a href="https://github.com/Solrikk/DataDresser/blob/main/README_JP.md">Japanese</a> | <a href="README_KR.md">Korean</a> | <a href="README_CN.md">Chinese</a> </h3> </div>

-----------------

# DataDresser

 🔎 _**DataDresser**_ is a web application built using FastAPI, designed to allow users to upload Excel files for automatic transformation according to specified rules and templates. The application performs data transformations within the file, applying various transformations to column values, such as unit conversion and proper depiction of product expiration terms.

## How It Works
Users can upload their Excel file through a simple web interface. Upon uploading, the file undergoes several transformations:

## Applying styling templates
Capitalizing all string values
Converting measurement units (e.g., 'm' to 'cm')
Accurately displaying verbal expressions of expiration terms (e.g., '1 year', '2 years', '5 years')
After the transformations, the original file is saved with the applied changes and returned to the user.

## Technologies
FastAPI: For building the web application and handling HTTP requests.
Pandas and OpenPyXL: For reading, transforming, and writing Excel files.
Python: As the primary programming language.
