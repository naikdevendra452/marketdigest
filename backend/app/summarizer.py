import re

def naive_summarize(text:str, max_bullets:int=3) -> str:
    # very basic: split into sentences, pick first few
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    sents = [s for s in sents if s]
    return " • " + " • ".join(sents[:max_bullets])
