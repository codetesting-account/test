import requests
import gensim
import gensim.downloader as api
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import nltk

# Download pretrained Word2Vec model (Google's trained model)
nltk.download('punkt')
model = api.load("word2vec-google-news-300")  # Large, but very effective

def expand_query(query):
    words = word_tokenize(query.lower())
    expanded_terms = set(words)
    
    for word in words:
        if word in model.key_to_index:  # Check if word exists in Word2Vec vocab
            similar_words = model.most_similar(word, topn=3)  # Get top 3 similar words
            expanded_terms.update([w[0] for w in similar_words])
    
    return " OR ".join(expanded_terms)

def search_stack_overflow(query):
    url = f"https://api.stackexchange.com/2.3/search?order=desc&sort=relevance&intitle={query}&site=stackoverflow"
    response = requests.get(url)
    data = response.json()
    
    results = []
    for item in data.get("items", [])[:5]:  # Get top 5 results
        results.append({
            "title": item["title"],
            "link": item["link"],
            "question_id": item["question_id"]
        })
    return results

def extract_code_snippets(question_id):
    url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody"
    response = requests.get(url)
    data = response.json()
    
    code_snippets = []
    for item in data.get("items", []):
        soup = BeautifulSoup(item["body"], "html.parser")
        code_blocks = soup.find_all("code")
        for code in code_blocks:
            code_snippets.append(code.text.strip())
    
    return code_snippets[:3]  # Return top 3 snippets

# Main Execution
user_query = input("Enter a coding query: ")
expanded_query = expand_query(user_query)
print(f"Expanded Query: {expanded_query}")

results = search_stack_overflow(expanded_query)
if results:
    print("\nTop Stack Overflow Results:")
    for i, res in enumerate(results):
        print(f"{i+1}. {res['title']} - {res['link']}")
        code_snippets = extract_code_snippets(res['question_id'])
        if code_snippets:
            print("\nCode Snippets:")
            for snippet in code_snippets:
                print(f"\n{snippet}\n" + "-"*50)
else:
    print("No results found!")
