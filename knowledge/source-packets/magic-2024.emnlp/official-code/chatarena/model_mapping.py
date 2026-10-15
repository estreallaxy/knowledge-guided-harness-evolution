backend_model_mappings={
    "groq-chat":[
        "llama3-8b-8192",
        "llama3-70b-8192"],
    "local-chat":[
        "llama3-8b-8192-finetune",
        "llama3-8b-8192-instruct-finetune",
        "llama3-8b-8192-instruct-finetune-alldata",
        "llama3-8b-8192-instruct-finetune-idata"],
    "openai-chat":[
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4o",
        "gpt-4-turbo",
        "o1-preview"
    ]
}

def check_model_available(model_name):
    for back in backend_model_mappings:
        for mn in backend_model_mappings[back]:
            if model_name == mn or model_name.replace("-pgm",'') == mn:
                return back
    return None
