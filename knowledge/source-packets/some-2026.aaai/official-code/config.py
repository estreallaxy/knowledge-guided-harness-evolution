#  Embedding model configuration
embedding_model_path = "Qwen/Qwen3-Embedding-4B" # or locally "./models/Qwen3-Embedding-4B"
embedding_model_device = "cpu"

knowledge_path = "./database/knowledge_data/knowledge_base.json"
knowledge_emb_path = "./database/emb_data/knowledge_base.npy"

# Data parse
post_key2entry = {"unique_id": "unique_id",
                  "content": "内容", 
                  "platform_name": "发布平台", 
                  "title": "标题", 
                  "post_publish_time": "发布时间", 
                  "ocr": "OCR", 
                  "nickname": "发布用户",
                  "public_location": "发布地点"}
weibo_key2entry = {"id": "id",
                   "text": "内容", 
                   "created_time": "发布时间", 
                   "source": "来自", 
                   "region_name": "发布地点", 
                   "reposts_count": "转发数", 
                   "comments_count": "评论数", 
                   "attitudes_count": "点赞数", 
                   "pic_num": "图片数量",
                   "pictures": "图片",
                   "video": "视频",
                   "rca_list": "rca_list"}
topic_key2entry = {"title": "标题",
                    "desc": "描述",
                    "content": "内容", 
                    "nickname": "发布者", 
                    "platform": "发布平台", 
                    "post_create_time": "发布时间"}

# Agent configuration
MAX_LLM_CALL_PER_RUN = 20
