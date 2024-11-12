import praw # type: ignore
import xmltodict # type: ignore
import urllib.request
import datetime
import pickle
from Document import Document
from Author import Author
from Corpus import Corpus

# Initialize Reddit API
reddit = praw.Reddit(client_id='RGNgO8xN9cY2NBCrPipjwQ', client_secret='LePhMMz_Lw4Oya8w5s1D-Yy0eSNGyA', user_agent='ABDOURAHMANE TIMERA')

# Fetch Reddit posts
hot_posts = reddit.subreddit('football').hot(limit=20)
texte_redit = []
for post in hot_posts:
    texte = post.title + " " + post.selftext.replace('\n', '')
    texte_redit.append(("reddit", texte, post))  # Including post object

# Fetch Arxiv posts
textes_Arxiv = []
query = "football"
url = 'http://export.arxiv.org/api/query?search_query=all:' + query + '&start=0&max_results=100'
url_read = urllib.request.urlopen(url).read()
data = url_read.decode()
dico = xmltodict.parse(data)
docs = dico['feed']['entry']

for d in docs:
    texte = d['title'] + ". " + d['summary'].replace("\n", " ")
    textes_Arxiv.append(("arxiv", texte, d))  # Including doc object

# Combine and filter corpus
corpus = texte_redit + textes_Arxiv
corpus_plus100 = [doc for doc in corpus if len(doc[1]) > 100]  # Filter based on text length

# Initialize collection and process documents
collection = []
for nature, text, doc in corpus_plus100:
    if nature == "reddit":
        titre = doc.title.replace("\n", '')
        auteur = str(doc.author)
        date = datetime.datetime.fromtimestamp(doc.created_utc).strftime("%Y/%m/%d")
        url = "https://www.reddit.com" + doc.permalink
        texte = doc.selftext.replace("\n", "")
        doc_classe = Document(titre, auteur, date, url, texte)
        collection.append(doc_classe)
        
    elif nature == "arxiv":
        titre = doc["title"].replace('\n', '')
        try:
            authors = ", ".join([a["name"] for a in doc["author"]])
        except:
            authors = doc["author"]["name"]
        summary = doc["summary"].replace("\n", "")
        date = datetime.datetime.strptime(doc["published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d")
        doc_classe = Document(titre, authors, date, doc["id"], summary)
        collection.append(doc_classe)

# Create id2doc mapping
id2doc = {i: doc.titre for i, doc in enumerate(collection)}

# Build Corpus
corpus = Corpus()
for doc in collection:
    corpus.add(doc)



with open("corpus.pkl", "wb") as f:
    pickle.dump(corpus, f)


with open("corpus.pkl", "rb") as f:
    loaded_corpus = pickle.load(f)
    
print("Loaded corpus:", loaded_corpus.id2doc)

