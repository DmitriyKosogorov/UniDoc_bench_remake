conda activate YOUR_ENV_NAME;

root_path="YOUR_DATA_PATH/final_database/healthcare"


#

cd YOUR_PROJECT_PATH/src/baselines/VRAG;

python search_engine/search_engine_api.py \
    --dataset_dir $root_path
