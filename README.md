# Bachelor tesis

## Description

This project consists of two main parts:

### Backend

The backend is responsible for:

Collecting projects from a structured folder system. Extracting metadata, keywords, and images from reports (Markdown/PDF). Processing and classifying data using NLP tools. Uploading structured data to Firebase Realtime Database and Storage

### Frontend

#### need to be added

#### Live app: https://bachelor-cc64fb.pages.fi.muni.cz/#/home

The frontend depends entirely on correctly processed and uploaded backend data.

#### Important

_The frontend does NOT process data itself. All data must be prepared and uploaded via the backend pipeline._

## Deploy app

link: https://bachelor-cc64fb.pages.fi.muni.cz/#/home

## Add new projects

- Create a folder for each semester using the format: podzim2026, podzim2027, etc.
- Add all project files to the corresponding semester folder.

## Add new categories or technologies

\* Manual adding

- Add new categories to _tags.yaml_ in _../backend/data/_
  - Include all relevant keywords for each category

- Add new technologies to _tech_terms.yaml_ in _../backend/data/_
  - Include all variations of how the technology may appear in text

\* Automatic adding(need to be checked)

- This feature may need refactoring and might not fully support the new format.

## Add projects to database

1. In your main file, initialize the path and pipeline:

```
    path = Path(r"C:\example\path")
    pipeline = Pipeline(
        root_dir=Path(path),
    )
```

2. Run the upload process:

```
    pipeline.run_upload()
```

This will automatically extract information from reports and upload it to the database in the correct format.
If something is missing, check the logs for details.

## Installation

```
pip install -r requirements.txt
```

## Authors and acknowledgment

### need to be added

## License

### need to be added
