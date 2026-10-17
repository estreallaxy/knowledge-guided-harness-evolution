import json
from sklearn.metrics import cohen_kappa_score
def read_human_scores(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item["score"] for item in data]

def read_llm_scores(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item["guidance"]["score"] for item in data]


if __name__ == "__main__":
    file1 = "dialogue_guidance_by_llm_eval.json"
    file2 = "dialogue_guidance_by_human_eval.json"
    scores1 = read_llm_scores(file1)
    scores2 = read_human_scores(file2)
    print(scores1)
    print(scores2)
    print(cohen_kappa_score(scores2, scores1, weights='quadratic'))


