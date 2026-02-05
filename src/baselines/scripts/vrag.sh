cd YOUR_PROJECT_PATH/src/baselines/VRAG/demo;
conda activate YOUR_ENV_NAME;

name_str="commerce_manufacturing"
model_name="gpt-4.1"
repeated_nums=10
root_folder="YOUR_DATA_PATH/final_database/${name_str}"
save_path="YOUR_DATA_PATH/QA/baseline/vrag/${name_str}_paper_sim${repeated_nums}_cost.json"
read_path="YOUR_DATA_PATH/QA/synthesized_qa/paper_qa/${name_str}_synthesized_qa_template_remained_filtered_balanced_rewritten_2.json"


python vrag_agent.py \
    --model_name $model_name \
    --root_folder $root_folder \
    --read_path $read_path \
    --save_path $save_path \
    --repeated_nums $repeated_nums