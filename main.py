from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
import pandas as pd
import numpy as np
import os
from openpyxl import load_workbook
from copy import copy

app = FastAPI()


def read_template(filename):
  template_df = pd.read_excel(filename, engine='openpyxl')
  return template_df


def transform_value(value):
  if pd.isnull(value):
    return None
  if 'м' in str(value):
    return str(value).replace('м', ' см').replace('.', ',').capitalize()
  if 'mm' in str(value):
    return str(float(value.replace('mm', '')) / 10).replace(
        '.', ',') + ' см'.capitalize()
  return value.capitalize()


def transform_data(df):
  for column in df.columns:
    df[column] = df[column].apply(lambda x: str(x).capitalize()
                                  if pd.notnull(x) else None)
  return df


def convert_years(value):
  if pd.isnull(value):
    return None
  try:
    value = int(value)
    if value == 1:
      return f"{value} год".capitalize()
    elif 1 < value % 10 < 5 and (value % 100 < 10 or value % 100 > 20):
      return f"{value} года".capitalize()
    else:
      return f"{value} лет".capitalize()
  except ValueError:
    return value.capitalize()


def split_colors(df):
  if 'Цвет' in df.columns:
    df_colors = df['Цвет'].str.split('/| и ', expand=True)
    for i, col in enumerate(df_colors.columns):
      df[f'Цвет-{i+1}'] = df_colors[col].str.strip().apply(
          lambda x: x.capitalize() if pd.notnull(x) else None)
    df.drop(columns=['Цвет'], inplace=True)
  return df


def apply_transformations(df):
  df = transform_data(df)
  df = split_colors(df)
  for column in df.columns:
    if 'срок годности' in column.lower():
      df[column] = df[column].apply(convert_years)
  return df


def map_brand_to_id(df, brand_mapping_filename='Бренд.xlsx'):
  brand_df = pd.read_excel(brand_mapping_filename, engine='openpyxl')
  brand_mapping = dict(zip(brand_df['Название'], brand_df['ID']))
  if 'Бренд' in df.columns:
    df['Бренд_ID'] = df['Бренд'].map(brand_mapping).fillna('Unknown ID')
  return df


def convert_to_template(filename, template_filename='Шаблон1.xlsx'):
  uploaded_df = pd.read_excel(filename, engine='openpyxl')
  transformed_df = apply_transformations(uploaded_df)
  transformed_df = map_brand_to_id(transformed_df)

  converted_dir = "converted_uploads"
  os.makedirs(converted_dir, exist_ok=True)
  transformed_filename = f"{converted_dir}/{os.path.basename(filename)}"

  transformed_df.to_excel(transformed_filename, index=False, na_rep="")

  return transformed_filename


@app.get("/", response_class=HTMLResponse)
async def main():
  content = """
    <html>
        <body>
            <form action="/upload/" enctype="multipart/form-data" method="post">
            <input name="file" type="file">
            <input type="submit">
            </form>
        </body>
    </html>
    """
  return content


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
