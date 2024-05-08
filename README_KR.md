<div align="center">
  <img src="https://github.com/Solrikk/DataBrain/blob/main/assets/gif/3d-isometric-research-of-statistical-data-and-analytics.gif" width="30%"/>
</div>


<div align="center"> <h3> <a href="https://github.com/Solrikk/DataBrain/blob/main/README.md">⭐English⭐</a> | <a href="https://github.com/Solrikk/DataBrain/blob/main/README_RU.md">Russian</a> | <a href="https://github.com/Solrikk/DataBrain/blob/main/README_GE.md">German</a> | <a href="https://github.com/Solrikk/DataBrain/blob/main/README_JP.md">Japanese</a> | <a href="README_KR.md">Korean</a> | <a href="README_CN.md">Chinese</a> </h3> </div>

-----------------

# Data Brain

Data Brain is a powerful FastAPI application designed to transform and manipulate Excel files specifically tailored for e-commerce data. It automates the process of data normalization, transformation, and enrichment to facilitate easy handling and preparation of product catalogs.

## Features
- **Excel File Processing**: Utilizes `openpyxl` for robust Excel file reading and writing.
- **Normalization and Transformation**: Standardizes column names and applies transformations across datasets to maintain consistency.
- **Data Enrichment**: Enhances data entries by appending additional information, such as merging product name and color.
- **Brand and Section Mapping**: Implements mappings from brand names to IDs and categorizes products into sections based on textual similarity.
- **Interactive File Upload**: Features a simple and intuitive web interface for uploading and automatically processing files.

### FastAPI Framework

- **Asynchronous Support**: FastAPI utilizes Starlette for its web framework, allowing for asynchronous request handling, which improves the application's performance and scalability.
- **Type Hints and Automatic Validation**: Utilizes Python type hints to validate data, automatically generating detailed error messages and reducing the development time for data validation logic.
- **OpenAPI and Swagger UI**: Automatically generates a comprehensive and interactive API documentation, enabling easy testing and debugging of API endpoints.

### Data Processing with Pandas and NumPy

- **Pandas**: Employs Pandas for efficiently handling and transforming data frames. This includes reading Excel files, manipulating columns, and applying transformations. Pandas' powerful functionalities are utilized for complex data operations like normalizing column names and appending data.
- **NumPy**: In conjunction with Pandas, NumPy is used for numerical operations where needed, enhancing the performance of data manipulation tasks.

### Excel Manipulation with Openpyxl

- **Excel File Support**: Leveraging `openpyxl`, a Python library to read and write Excel 2010 xlsx/xlsm/xltx/xltm files, the application handles the input and output of Excel files, allowing for the processing of complex spreadsheets.

### Machine Learning for Text Similarity

- **TF-IDF Vectorizer**: Used from the scikit-learn library, the TF-IDF Vectorizer transforms text data into a matrix of TF-IDF features. This is critical for comparing text similarity, especially in mapping product sections based on similarity to predefined categories.
- **Cosine Similarity**: Utilizes the cosine similarity measure to find the most relevant category for each product by comparing the TF-IDF vectors of product descriptions with those of predefined categories.

### Deployment and Environment Management

- **Nix Package Manager**: Though not explicitly detailed in the code fragments, if utilized, Nix can significantly simplify the deployment process and environment management, ensuring consistency across development and production environments.

## Noteworthy Technical Features

### Data Normalization and Transformation

The application performs several sophisticated data transformation steps, including:
- Normalizing column names to follow a consistent schema.
- Transforming text data to ensure consistency, such as capitalizing and merging specific fields for better readability or processing logic.

### Dynamic Data Mapping

The principle of mapping data, such as brand names to IDs and sections by textual similarity, showcases an application of machine learning techniques in a traditional data processing tool, enhancing automatic categorization and tagging.

### Modular Design

The application's structure allows for easy extension and modification. Each function, from reading Excel files to applying transformations and mappings, is defined in a modular way, promoting reusability and maintainability.

