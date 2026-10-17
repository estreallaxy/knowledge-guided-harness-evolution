import json
from Levenshtein import distance
import pandas as pd
import re
from openai import OpenAI

# mathvista
def calculate_accuracy(final_answers: list, entries: list, output_file: str = None,  correct_ids_file: str = None, ignore_empty=True, precision=2):
    results = []
    correct_pids = []

    metadata_fields = ['question_type', 'answer_type', 'language',
                       'source', 'category', 'task', 'context', 'grade']

    for answer, entry in zip(final_answers, entries):
        meta = entry.get('metadata', {})
        q_type = entry.get('question_type', meta.get('question_type', ''))
        a_type = entry.get('answer_type', meta.get('answer_type', ''))
        choices = entry.get('choices', [])
        correct_answer = str(entry.get('answer', '')).strip().lower()
        pid = entry.get('pid', '')

        normalized = normalize_answer(
            answer,
            choices,
            q_type,
            a_type,
            entry.get('precision', precision),
            ignore_empty
        )
        print(normalized)
        correct = normalized.lower() == correct_answer if normalized else False

        if correct:
            correct_pids.append(str(int(pid)-1))

        results.append({
            'prediction': normalized,
            'true_answer': entry.get('answer', ''),
            'correct': correct,
            **{k: meta.get(k, entry.get(k, '')) for k in metadata_fields},
            'skills': meta.get('skills', [])
        })
    if correct_ids_file:
        try:
            with open(correct_ids_file, 'w') as f:
                json.dump(correct_pids, f, indent=2)
            print(f"saved: {correct_ids_file}")
        except Exception as e:
            print(f"failed: {str(e)}")

    df = pd.DataFrame(results)
    total = len(df)
    correct = df['correct'].sum()
    overall_acc = correct / total if total else 0.0

    details = {}
    for field in metadata_fields + ['skills']:
        if field == 'skills':
            groups = group_skills(df)
        else:
            groups = df.groupby(field)

        details[field] = {}
        for key in groups.groups if field != 'skills' else groups:
            group = groups.get_group(key) if field != 'skills' else groups[key]
            cnt = len(group)
            corr = group['correct'].sum()
            acc = corr / cnt if cnt else 0.0
            details[field][key] = {
                'correct': int(corr),
                'total': int(cnt),
                'accuracy': round(acc, 4)
            }

    result_dict = {
        "overall_accuracy": round(overall_acc, 4),
        "details": details
    }

    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result_dict, f, indent=2)

    return result_dict


def normalize_answer(prediction, choices, q_type, a_type, precision, ignore_empty):
    try:
        if q_type == 'multi_choice':
            prediction = str(prediction).strip().lower()
            choices_lower = [str(c).strip().lower() for c in choices]
            
            letter_match = re.search(r'\b([a-z])\b', prediction, flags=re.IGNORECASE)
            if letter_match:
                letter = letter_match.group(1).lower()
                if len(choices) > ord(letter) - ord('a') >= 0:
                    return choices[ord(letter) - ord('a')]

            for choice, choice_lower in zip(choices, choices_lower):
                if choice_lower in prediction:
                    return choice

            return get_most_similar(prediction, choices_lower, choices)

        if a_type in ['integer', 'float']:
            try:
                num = float(prediction)
                if a_type == 'integer':
                    return str(int(num))
                # print(round(num, int(precision)))
                return str(round(num, int(precision)))
            except:
                return None

        return str(prediction).strip()

    except (ValueError, TypeError):
        return None if ignore_empty else ""


def get_most_similar(pred_lower, choices_lower, original_choices):
    pred_lower = str(pred_lower).lower()
    scores = [(distance(pred_lower, c.lower()), i) for i, c in enumerate(original_choices)]
    scores.sort(key=lambda x: (x[0], -len(original_choices[x[1]])))
    return original_choices[scores[0][1]]


def group_skills(df):
    skills = set()
    for sublist in df['skills'].dropna():
        skills.update(sublist)
    return {skill: df[df['skills'].apply(lambda x: skill in x)] for skill in skills}


def judge(prompt):
    client = OpenAI(api_key="", base_url="")

    system_prompt = r"""
    You are a strict answer evaluation expert responsible for determining whether a multiple-choice answer is correct.

You will receive the following information:
	•	Options (options): A list containing multiple answer choices.
	•	Correct answer (true_answer): The correct choice (e.g., “D”).
	•	Final answer (final_answer): The user’s selected answer (e.g., “Cl[C-]Cl”).

Your task is to:
	1.	Identify the correct answer content from the options list based on true_answer.
	2.	Compare final_answer with the identified correct answer.
	3.	If they match, return true; otherwise, return false. Only return true or false, without any additional explanation.
    
    Output it in JSON format. 

    EXAMPLE JSON OUTPUT:
    {
        "judge": "true/false"
    }
    """

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}]

    response = client.chat.completions.create(
        model="",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    return json.loads(response.choices[0].message.content)


def process_data(data_path, file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    true_count = 0
    total = len(data)
    cid = []

    options_list = pd.read_parquet(data_path, columns=['options'])['options'].tolist()
    i=0
    for item in data:
        final_a = item['final_answer']
        true_a = item['true_answer']
        id = item['id']
        option = options_list[i]
        i+=1
        prompt = f"options: {option}\n true_answer: {true_a}\n final_answer: {final_a}\n"
        output = judge(prompt)['judge']
        print(output)
        # 调用评估函数
        if output=='true' or output == 'True':
            cid.append(str(id))
            true_count += 1

    return true_count, total, cid

def final_process(data_path, file_path):
    true_count, total, cid = process_data(data_path, f"{file_path}/agent_output.json")


    with open(f"{file_path}/correct_ids.json", "w") as f:
        json.dump(cid, f, indent=2)

if __name__ == "__main__":

    final_process("Dataset/EMMA/ChemistryMini.parquet", "Output/EMMA/Gemini2-flash/ChemistryMini")

