from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

app = FastAPI()


def load_html_file(file_path):
  with open(file_path, 'r', encoding='utf-8') as file:
    return file.read()


def normalize_column_names(df):
  other_columns_to_normalize = {
      'Разделы': 'Разделы',
      'Бренд': 'Бренд',
      'Наименование': 'Наименование',
      'Артикул': 'Артикул',
      'Цвет': 'Цвет'
  }
  for original_col, normalized_col in other_columns_to_normalize.items():
    found_columns = [col for col in df.columns if original_col in col]
    for col in found_columns:
      if col != normalized_col:
        df.rename(columns={col: normalized_col}, inplace=True)
  return df


def transform_data(df):
  for column in df.columns:
    df[column] = df[column].apply(lambda x: str(x).capitalize()
                                  if pd.notnull(x) else x)
  return df


def extend_product_name(df):
  if 'Цвет' in df.columns and 'Наименование' in df.columns:
    additional_columns = [
        'Тип товара', 'Размеры (см)', 'Бренд', 'Коллекция', 'Артикул'
    ]

    def combine_columns(row):
      name = str(row['Наименование'])
      additions = [
          str(row[col]) for col in additional_columns
          if col in df.columns and str(row[col]).lower() != 'nan'
      ]
      combined = f"{name} {' '.join(additions)}"
      return ' '.join(sorted(set(combined.split()),
                             key=combined.split().index))

    df['Наименование'] = df.apply(combine_columns, axis=1)
  return df


def apply_transformations(df):
  df = normalize_column_names(df)
  df = transform_data(df)
  df = extend_product_name(df)
  return df


def map_brand_to_id(df, brand_mapping_filename='Бренд.xlsx'):
  brand_df = pd.read_excel(brand_mapping_filename, engine='openpyxl')
  brand_mapping = dict(zip(brand_df['Название'], brand_df['ID']))
  if 'Бренд' in df.columns:
    df['Бренд_ID'] = df['Бренд'].map(brand_mapping).fillna('Unknown ID')
  return df


def map_sections_by_similarity(df, section_mapping_filename='Разделы.xlsx'):
  section_df = pd.read_excel(section_mapping_filename, engine='openpyxl')
  if 'Разделы' in df.columns:
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix_section = tfidf_vectorizer.fit_transform(
        section_df['Название'])
    tfidf_matrix_uploaded = tfidf_vectorizer.transform(df['Разделы'])

    cosine_similarities = linear_kernel(tfidf_matrix_uploaded,
                                        tfidf_matrix_section)
    df['Разделы'] = [
        section_df['Название'].iloc[np.argmax(row)]
        if max(row) > 0 else 'Без категории' for row in cosine_similarities
    ]
  return df


def convert_to_template(filename, template_filename='Шаблон1.xlsx'):
  uploaded_df = pd.read_excel(filename, engine='openpyxl')
  transformed_df = apply_transformations(uploaded_df)
  transformed_df = map_brand_to_id(transformed_df)
  transformed_df = map_sections_by_similarity(transformed_df)

  converted_dir = "converted_uploads"
  os.makedirs(converted_dir, exist_ok=True)
  transformed_filename = f"{converted_dir}/{os.path.basename(filename)}"
  transformed_df.to_excel(transformed_filename, index=False, na_rep="")
  return transformed_filename


@app.get("/", response_class=HTMLResponse)
async def main():
  html_content = load_html_file('index.html')
  return HTMLResponse(content=html_content)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
  contents = await file.read()
  upload_dir = "uploads"
  os.makedirs(upload_dir, exist_ok=True)
  file_path = f"{upload_dir}/{file.filename}"
  with open(file_path, "wb") as f:
    f.write(contents)
  converted_filename = convert_to_template(file_path)
  return FileResponse(path=converted_filename,
                      filename=os.path.basename(file.filename))
