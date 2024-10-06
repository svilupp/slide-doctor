import requests
from transformers import pipeline

# Constants
API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_SEARCH_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"

# Maximum token length for the model (adjust if necessary)
MAX_MODEL_LENGTH = 1024  # Tokens

# Function to chunk text
def chunk_text(text, chunk_size):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])

# Function to make a search query
def brave_search(query, country="us", search_lang="en", count=10, offset=0, safesearch="moderate", freshness=None):
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": API_KEY
    }
    
    # Clean up the query by removing special characters
    query = query.replace(".", "").replace(",", "").strip()
    
    # Query parameters
    params = {
        "q": query,
        "country": country,
        "search_lang": search_lang,
        "count": count,
        "offset": offset,
        "safesearch": safesearch
    }
    
    # Optionally add freshness filter if provided
    if freshness:
        params["freshness"] = freshness
    
    # Send request to Brave API
    response = requests.get(BRAVE_SEARCH_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Function to perform fact-checking using NLI
def fact_check(statement):
    # Perform the search
    search_results = brave_search(query=statement, count=5, freshness="pw")

    # Aggregate snippets from both description and extra_snippets
    snippet_url_pairs = []
    
    for result in search_results.get("web", {}).get("results", []):
        # Add 'description' if available
        if result.get('description'):
            snippet_url_pairs.append((result['description'], result.get('url', 'No URL')))
        # Add all 'extra_snippets' if available
        if result.get('extra_snippets'):
            for snippet in result['extra_snippets']:
                snippet_url_pairs.append((snippet, result.get('url', 'No URL')))

    # Initialize the NLI pipeline
    nli_model = pipeline("text-classification", model="facebook/bart-large-mnli")
    
    # Fact-check each snippet against the statement
    label_dict = {"ENTAILMENT": None, "CONTRADICTION": None, "NEUTRAL": None}

    for snippet, url in snippet_url_pairs:
        # Run the NLI model to check the relationship between the snippet and the statement
        result = nli_model(f"{statement} </s> {snippet}")[0]
        label = result['label'].upper()
        
        # Update the label_dict only if the score is higher than any existing entry
        if label in label_dict:
            if label_dict[label] is None or result['score'] > label_dict[label][1]:
                label_dict[label] = (snippet, result['score'], url)

    return label_dict

# Example usage
if __name__ == "__main__":
    # Input the text description to fact-check
    statement_to_check = "The Eiffel Tower is the tallest structure in Paris"

    # Perform fact-checking
    try:
        fact_check_results = fact_check(statement_to_check)
        
        # Print the results
        print("\nFact-Check Results:")
        for label, result in fact_check_results.items():
            if result:
                snippet, score, url = result
                print(f"\nLabel: {label}\nSnippet: {snippet}\nScore: {score:.4f}\nSource: {url}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
