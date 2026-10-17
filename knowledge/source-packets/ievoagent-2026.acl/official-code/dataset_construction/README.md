Some useful commands examples (make sure your working path is under `dataset_construction` and the conda environment is `acl2026_data):
+ python data_constr.py pre_filter --src ../dataset/lmsys-chat-1m/data --dst ./filtered --name lmsys-chat-1m-geq8 --min_turn 8 --shuffle
+ python data_constr.py pre_filter --src ../dataset/WildChat-1M/data --dst ./filtered --name WildChat-1M-geq8 --min_turn 8 --shuffle
+ python data_constr.py construct_final --src ./filtered/WildChat-1M-geq8.parquet --prompt_file ./prompt_single_new.txt
+ python data_constr.py construct_final --src ./filtered/lmsys-chat-1m-geq8.parquet --prompt_file ./prompt_single_new.txt
+ python data_constr.py post_filter --src ./filtered/WildChat-1M-geq8_final --dst ../dataset/our_dataset/WildChat
+ python data_constr.py post_filter --src ./filtered/lmsys-chat-1m-geq8_final --dst ../dataset/our_dataset/lmsys