import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# 패턴: 주어 + 동사 + 목적어
pattern = [
    {"DEP": "nsubj"},    # 주어
    {"POS": "VERB"},     # 동사
    {"DEP": "dobj"}      # 목적어
]
matcher.add("SVO", [pattern])

text = "Steve Jobs founded Apple in 1976."
doc = nlp(text)

matches = matcher(doc)
for match_id, start, end in matches:
    span = doc[start:end]
    subject = [tok.text for tok in span if tok.dep_ == "nsubj"]
    verb = [tok.text for tok in span if tok.pos_ == "VERB"]
    obj = [tok.text for tok in span if tok.dep_ == "dobj"]
    print(f"Triple: ({subject[0]}, {verb[0]}, {obj[0]})")
    
    
    
{
  "sentence": "Steve Jobs founded Apple in 1976.",
  "head": {"word": "Steve Jobs"},
  "tail": {"word": "Apple"},
  "relation": "founded"
}

import openai

openai.api_key = "api-key"

def extract_triples(sentence):
    prompt = f"""
    Extract a triple (subject, relation, object) from the following sentence:
    "{sentence}"
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response['choices'][0]['message']['content']

# 테스트
text = "Elon Musk acquired Twitter in 2022."
print(extract_triples(text))