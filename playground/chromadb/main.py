import chromadb
chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="my_collection")

collection.add(
    ids=["id1", "id2", "id3"],
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges",
        "Capital of Iran is Tehran"
    ]
)

results = collection.query(
    query_texts=["This is a query document about Persians"], # Chroma will embed this for you
    n_results=3 # how many results to return
)
print(results)