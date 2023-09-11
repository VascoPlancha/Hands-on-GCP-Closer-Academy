# Install dependencies
poetry install --with dev,docs

# Activate environment
sh ./.venv/bin/activate

# Login into GCP
gcloud auth application-default login