from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
import pandas as pd
import os
from openpyxl import load_workbook

app = FastAPI()


def read_template(filename):
  template_df = pd.read_excel(filename, engine='openpyxl')
  return template_df


def transform_value(value):
  if pd.isnull(value):
    return value
  if 'м' in str(value):
    return str(value).replace('м', ' см').replace('.', ',')
  if 'mm' in str(value):
    return str(float(value.replace('mm', '')) / 10).replace('.', ',') + ' см'
  return value


def transform_data(df):
  for column in df.columns:
    if 'м' in column or 'mm' in column:
      df[column] = df[column].apply(transform_value)
    else:
      df[column] = df[column].astype(str).str.upper()
  return df


def convert_years(value):
  if pd.isnull(value):
    return value
  try:
    value = int(value)
    if value == 1:
      return f"{value} год"
    elif 1 < value % 10 < 5 and (value % 100 < 10 or value % 100 > 20):
      return f"{value} года"
    else:
      return f"{value} лет"
  except ValueError:
    return value


def apply_transformations(df):
  df = transform_data(df)
  for column in df.columns:
    if 'срок годности' in column.lower():
      df[column] = df[column].apply(convert_years)
  return df


def convert_to_template(filename, template_filename='Шаблон.xlsx'):
  uploaded_df = pd.read_excel(filename, engine='openpyxl')
  template_workbook = load_workbook(template_filename)
  template_sheet_name = template_workbook.sheetnames[0]

  template_df = read_template(template_filename)
  transformed_df = apply_transformations(uploaded_df)

  converted_dir = "converted_uploads"
  os.makedirs(converted_dir, exist_ok=True)
  transformed_filename = f"{converted_dir}/{os.path.basename(filename)}"

  transformed_df.to_excel(transformed_filename,
                          sheet_name=template_sheet_name,
                          index=False)

  transformed_workbook = load_workbook(transformed_filename)
  transformed_sheet = transformed_workbook[template_sheet_name]
  template_sheet = template_workbook[template_sheet_name]

  for row in template_sheet.iter_rows():
    for cell in row:
      corresponding_cell = transformed_sheet[cell.coordinate]
      corresponding_cell.font = copy(cell.font)
      corresponding_cell.border = copy(cell.border)
      corresponding_cell.fill = copy(cell.fill)
      corresponding_cell.number_format = copy(cell.number_format)
      corresponding_cell.protection = copy(cell.protection)
      corresponding_cell.alignment = copy(cell.alignment)

  transformed_workbook.save(transformed_filename)
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
