conda activate YOUR_ENV_NAME
cd YOUR_PROJECT_PATH/src/evaluation/

name_str="healthcare"
method="text_image"
sim=5
input_file="YOUR_DATA_PATH/QA/baseline/${method}/${name_str}_paper_sim${sim}_cost.json"  # e.g., "/path/to/data/QA/baseline"
output_file="YOUR_DATA_PATH/QA/baseline/${method}/eval_2/${name_str}_paper_sim${sim}_cost.json"  # e.g., "/path/to/data/QA/baseline"
testsize=500

python evaluation_ragas.py \
  --input_file $input_file \
  --output_file $output_file \
  --testsize $testsize