# Install dependencies
poetry install --with dev

# Activate environment
sh ./.venv/bin/activate

# Login into GCP
gcloud auth application-default login