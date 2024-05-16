from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import zipfile

app = FastAPI()


def load_html_file(file_path):
  with open(file_path, 'r', encoding='utf-8') as file:
    return file.read()


def normalize_column_names(df, template_filename='Шаблон для импорта.xlsx'):
  manual_mapping = {'Бреншафт': 'Бренд', 'Цвета': 'Цвет'}
  template_df = pd.read_excel(template_filename)
  template_columns = list(template_df.columns)
  tfidf_vectorizer = TfidfVectorizer()
  tfidf_matrix_template = tfidf_vectorizer.fit_transform(template_columns)
  uploaded_columns = list(df.columns)
  tfidf_matrix_uploaded = tfidf_vectorizer.transform(uploaded_columns)
  cosine_similarities = linear_kernel(tfidf_matrix_uploaded,
                                      tfidf_matrix_template)
  for uploaded_idx, uploaded_col in enumerate(uploaded_columns):
    if uploaded_col in manual_mapping:
      best_match_column = manual_mapping[uploaded_col]
    else:
      matches = cosine_similarities[uploaded_idx]
      best_match_idx = matches.argmax()
      best_match_column = template_columns[best_match_idx]
    if uploaded_col != best_match_column:
      df = df.rename(columns={uploaded_col: best_match_column})
  return df


def transform_data(df):
  for column in df.columns:
    df[column] = df[column].apply(lambda x: str(x).capitalize()
                                  if pd.notnull(x) else x,
                                  result_type='expand')
  return df


def train_product_type_model(train_data_filename='train_data.xlsx'):
  train_df = pd.read_excel(train_data_filename)
  X = train_df['Наименование']
  y = train_df['Тип товара']
  tfidf_vectorizer = TfidfVectorizer()
  X_tfidf = tfidf_vectorizer.fit_transform(X)
  model = RandomForestClassifier()
  model.fit(X_tfidf, y)
  return model, tfidf_vectorizer


def predict_product_type(name, model, vectorizer):
  name_tfidf = vectorizer.transform([name])
  return model.predict(name_tfidf)[0]


def extend_product_name(df, model, vectorizer):
  if 'Наименование' in df.columns and 'Цвет' in df.columns:
    additional_columns = ['Бренд', 'Коллекция', 'Артикул', 'Размеры (см)']

    def combine_columns(row):
      name = str(row['Наименование'])
      color = str(row['Цвет'])
      brand = str(row['Бренд']) if 'Бренд' in row else ''
      collection = str(row['Коллекция']) if 'Коллекция' in row else ''
      article = str(row['Артикул']) if 'Артикул' in row else ''
      sizes = str(row['Размеры (см)']) if 'Размеры (см)' in row else ''
      product_type = predict_product_type(name, model, vectorizer)
      sizes_components = sizes.split('x')
      if len(sizes_components) == 3:
        sizes_str = f"{sizes_components[0]} x {sizes_components[1]} x {sizes_components[2]}"
      else:
        sizes_str = sizes
      combined = f"{product_type} {brand} {collection} {sizes_str} см {color}".replace(
          'nan', '').strip()
      return ' '.join(sorted(set(combined.split()),
                             key=combined.split().index))

    df['Наименование'] = df.apply(combine_columns, axis=1)
  return df


product_type_model, tfidf_vectorizer = train_product_type_model()


def apply_transformations(df, template_filename='Шаблон для импорта.xlsx'):
  df = normalize_column_names(df, template_filename)
  df = transform_data(df)
  df = extend_product_name(df, product_type_model, tfidf_vectorizer)
  return df


def map_brand_to_id(df, brand_mapping_filename='Бренд.xlsx'):
  brand_df = pd.read_excel(brand_mapping_filename)
  brand_mapping = dict(zip(brand_df['Название'], brand_df['ID']))
  if 'Бренд' in df.columns:
    df['Бренд_ID'] = df['Бренд'].map(brand_mapping).fillna('Unknown ID')
  return df


def map_sections_by_similarity(df, section_mapping_filename='Разделы.xlsx'):
  section_df = pd.read_excel(section_mapping_filename)
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


def convert_to_template(filename, template_filename='Шаблон для импорта.xlsx'):
  try:
    uploaded_df = pd.read_excel(filename)
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except FileNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
  except zipfile.BadZipFile:
    raise HTTPException(status_code=400,
                        detail="The uploaded file is not a valid Excel file.")
  template_df = pd.read_excel(template_filename)
  transformed_df = apply_transformations(uploaded_df, template_filename)
  transformed_df = map_brand_to_id(transformed_df)
  transformed_df = map_sections_by_similarity(transformed_df)
  for column in transformed_df.columns:
    if column in template_df.columns:
      template_df[column] = transformed_df[column]
  converted_dir = "converted_uploads"
  os.makedirs(converted_dir, exist_ok=True)
  transformed_filename = f"{converted_dir}/{os.path.basename(template_filename)}"
  template_df.to_excel(transformed_filename, index=False, na_rep="")
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
  try:
    converted_filename = convert_to_template(file_path)
  except HTTPException as http_exc:
    return HTMLResponse(
        content=f"<html><body><h2>Error: {http_exc.detail}</h2></body></html>",
        status_code=http_exc.status_code)
  return FileResponse(path=converted_filename,
                      filename=os.path.basename(converted_filename))
