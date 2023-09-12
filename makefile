simple-mlops-requirements:
	poetry export -f requirements.txt --output functions/simple_mlops/ingest_data/app/requirements.txt --without-hashes --with cloudfunctions
	poetry export -f requirements.txt --output functions/simple_mlops/train_model/app/requirements.txt --without-hashes --with cloudfunctions,model_train
