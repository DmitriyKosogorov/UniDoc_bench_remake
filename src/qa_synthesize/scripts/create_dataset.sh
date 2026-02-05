name_str="commerce_manufacturing"
root_str="YOUR_DATA_PATH/final_database/${name_str}"  # e.g., "/path/to/data/final_database"
testset_size=5000
save_path_str="YOUR_OUTPUT_PATH/synthesized_qa/paper_qa/${name_str}_synthesized_qa_template"  # e.g., "/path/to/output/synthesized_qa"
####

database_path="${root_str}_database"
folder_elements="${root_str}_elements"

conda init
conda activate YOUR_ENV_NAME
cd YOUR_PROJECT_PATH/src/qa_synthesize

python 1_kg_create.py \
   --name_str $name_str \
   --database_path $database_path

save_path="${save_path_str}.json"
python 2_qa_synthesize.py \
   --folder_elements $folder_elements \
   --name_str $name_str \
   --testset_size $testset_size \
   --output_file $save_path \
   --no_tab_in_chunk_text \
   --different_files_visited \
   --domain_name $name_str

qa_path="${save_path_str}.json"
python 3_filter_qa.py \
 --qa_path $qa_path \
 --folder_elements $folder_elements

file_path="${save_path_str}_remained.json"
python 4_filter_similarities.py \
   --file_path $file_path

file_path="${save_path_str}_remained_filtered.json"
python 5_balance.py \
   --file_path $file_path \
   --max_diff 0

file_path="${save_path_str}_remained_filtered_balanced.json"
mode="full"
file_path_save="${save_path_str}_remained_filtered_balanced_rewritten_2.json"
python 6_rewriting.py \
    --folder_elements $folder_elements \
    --file_path $file_path \
    --file_path_save $file_path_save \
    --mode $mode