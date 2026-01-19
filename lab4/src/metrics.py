from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge import Rouge

smooth = SmoothingFunction().method1
rouge = Rouge()


def compute_bleu(reference: str, generated: str):
    ref_tokens = [reference.split()]
    gen_tokens = generated.split()

    try:
        score = sentence_bleu(ref_tokens, gen_tokens, smoothing_function=smooth)
    except:
        score = 0.0

    return round(score, 4)


def compute_rouge(reference: str, generated: str):
    try:
        scores = rouge.get_scores(generated, reference)[0]
        return {
            "rouge-1": round(scores["rouge-1"]["f"], 4),
            "rouge-2": round(scores["rouge-2"]["f"], 4),
            "rouge-l": round(scores["rouge-l"]["f"], 4)
        }
    except:
        return {"rouge-1": 0, "rouge-2": 0, "rouge-l": 0}
