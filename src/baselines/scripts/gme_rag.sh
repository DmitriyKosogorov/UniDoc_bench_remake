name_str="healthcare"
load_index_path="./index/index_${name_str}_paper"
save_index_path="./index/index_${name_str}_paper"
folder="YOUR_DATA_PATH/final_database/${name_str}_database"
folder_elements="YOUR_DATA_PATH/final_database/${name_str}_elements"
question_path="YOUR_DATA_PATH/QA/synthesized_qa/paper_qa/${name_str}_synthesized_qa_template_remained_filtered_balanced_rewritten_2.json"
similarity_top_k=10
model_name="gpt-4.1"
save_path="YOUR_DATA_PATH/QA/baseline/gme/${name_str}_paper_sim${similarity_top_k}_cost.json"
load_index_img_path="./index/index_${name_str}_paper_gme"
save_index_img_path="./index/index_${name_str}_paper_gme"
folder_images="YOUR_DATA_PATH/final_database/${name_str}/img"

python image_rag_gme.py \
    --save_index_path $save_index_path \
    --folder $folder \
    --folder_elements $folder_elements \
    --question_path $question_path \
    --similarity_top_k $similarity_top_k \
    --model_name $model_name \
    --save_path $save_path \
    --load_index_path $load_index_path \
    --load_index_img_path $load_index_img_path \
    --save_index_img_path $save_index_img_path \
    --folder_images $folder_images