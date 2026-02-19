# ============================================================
# Streamlit RAG App — Policy Search Engine
# ============================================================
# - Loads PDFs from ./Policy documents
# - Builds/loads ChromaDB index in ./chroma_db
# - Retrieves Top-K passages and answers using OpenAI
# - Includes a "Rebuild index" option when PDFs change
# ============================================================

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction

import tiktoken
from pypdf import PdfReader

# -----------------------------
# 1) Page config FIRST (must be before other st.* calls)
# -----------------------------
st.set_page_config(page_title="XYZ Dummy Company India Employees Policy Search Engine", layout="wide")

# -----------------------------
# 2) Load API key + init OpenAI client
# -----------------------------
load_dotenv(override=True)
if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY not found. Put it in a .env file next to app.py.")
    st.stop()

client = OpenAI()

# -----------------------------
# 3) Config (relative paths so it runs anywhere)
# -----------------------------
DATA_DIR = Path("./Policy documents")
CHROMA_DIR = Path("./chroma_db")

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

CHUNK_TOKENS = 700
CHUNK_OVERLAP = 120
DEFAULT_TOP_K = 5

COLLECTION_NAME = "ntt_policy_rag"

# -----------------------------
# 4) Load PDFs (extract text page-by-page)
# -----------------------------
def load_pdfs(folder: Path):
    pages = []
    pdf_files = list(folder.rglob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in {folder.resolve()}. Add PDFs to ./Policy documents/")
    for pdf_path in pdf_files:
        reader = PdfReader(str(pdf_path))
        for page_num, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append({"text": text, "source": pdf_path.name, "path": str(pdf_path), "page": page_num})
    return pages

# -----------------------------
# 5) Token-based chunking
# -----------------------------
enc = tiktoken.get_encoding("cl100k_base")

def chunk_text(text: str, chunk_tokens: int, overlap: int):
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_tokens, len(tokens))
        chunk = enc.decode(tokens[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
        if end == len(tokens):
            break
    return chunks

def make_chunks(pages):
    out = []
    for p in pages:
        for i, ch in enumerate(chunk_text(p["text"], CHUNK_TOKENS, CHUNK_OVERLAP)):
            out.append({
                "chunk": ch,
                "source": p["source"],
                "path": p["path"],
                "page": p["page"],
                "chunk_id": f'{p["source"]}:p{p["page"]}:c{i}'
            })
    return out

# -----------------------------
# 6) OpenAI embedder for Chroma (batching reduces request count)
# -----------------------------
class OpenAIEmbedder(EmbeddingFunction):
    def __init__(self, client, model, batch_size=64):
        self.client = client
        self.model = model
        self.batch_size = batch_size

    def __call__(self, texts):
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i+self.batch_size]
            resp = self.client.embeddings.create(model=self.model, input=batch)
            embeddings.extend([item.embedding for item in resp.data])
        return embeddings

# -----------------------------
# 7) Create/load Chroma collection and index if needed
#    - "rebuild" deletes the collection and re-indexes (use when PDFs change)
# -----------------------------
@st.cache_resource
def get_collection(rebuild: bool):
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embedder = OpenAIEmbedder(client, EMBED_MODEL, batch_size=64)

    if rebuild:
        try:
            chroma_client.delete_collection(name=COLLECTION_NAME)
        except Exception:
            pass  # ok if collection didn't exist

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedder
    )

    if collection.count() == 0:
        pages = load_pdfs(DATA_DIR)
        chunks = make_chunks(pages)

        ids = [c["chunk_id"] for c in chunks]
        docs = [c["chunk"] for c in chunks]
        metas = [{"source": c["source"], "path": c["path"], "page": c["page"]} for c in chunks]

        BATCH = 256
        for i in range(0, len(ids), BATCH):
            collection.add(
                ids=ids[i:i+BATCH],
                documents=docs[i:i+BATCH],
                metadatas=metas[i:i+BATCH]
            )
    return collection

# -----------------------------
# 8) Retrieval + Answering (grounded responses with citations)
# -----------------------------
SYSTEM_PROMPT = """You are a policy assistant for India-based employees.
Answer ONLY using the provided policy excerpts.
If the answer is not in the excerpts, say: "I couldn't find this in the provided policies."
Keep the answer concise and practical.
Always end with citations in this format: (Source, page)."""

def retrieve(collection, query: str, top_k: int):
    res = collection.query(query_texts=[query], n_results=top_k)
    hits = []
    for doc, meta, _id in zip(res["documents"][0], res["metadatas"][0], res["ids"][0]):
        hits.append({"id": _id, "text": doc, "meta": meta})
    return hits

def answer(query: str, hits):
    context = "\n\n".join(
        [f"[{h['id']}] ({h['meta']['source']}, page {h['meta']['page']})\n{h['text']}" for h in hits]
    )
    user_input = f"Question: {query}\n\nPolicy excerpts:\n{context}"
    resp = client.responses.create(
        model=CHAT_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
    )
    return resp.output_text

# -----------------------------
# 9) Streamlit UI
# -----------------------------
st.title("XYZ Dummy company India Employees Policy Search Engine")
st.caption("Answers are generated only from indexed policy PDFs and include citations.")

rebuild = st.checkbox("Rebuild index (use this if PDFs changed)", value=False)
topk = st.slider("Top-K passages", 3, 10, DEFAULT_TOP_K)
q = st.text_input("Mention Policy name that you want to know about?", placeholder="e.g., anti-corruption policy")

# Load collection (cached). If rebuild is checked, we rebuild once.
try:
    collection = get_collection(rebuild)
    st.success(f"Vector DB ready. Indexed chunks: {collection.count()}")
except Exception as e:
    st.error(f"Indexing/DB error: {e}")
    st.stop()

if st.button("Search") and q.strip():
    with st.spinner("Searching..."):
        hits = retrieve(collection, q.strip(), top_k=topk)
        out = answer(q.strip(), hits)

    st.subheader("Answer")
    st.write(out)

    st.subheader("Sources")
    for h in hits:
        st.write(f"- {h['meta']['source']} | page {h['meta']['page']} | {h['id']}")
