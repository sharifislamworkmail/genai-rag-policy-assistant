🧠 GenAI RAG Policy Assistant
Retrieval-Augmented Generation (RAG) Based Policy Search Engine

📌 Project Overview

This project implements a Retrieval-Augmented Generation (RAG) system that enables users to query company policy documents using natural language.

Instead of relying only on a Large Language Model (LLM), this system:

    1. Converts policy documents into embeddings
    2. Stores them in a local vector database (ChromaDB)
    3. Retrieves relevant content for a query
    4. Uses GPT-4o-mini to generate grounded responses
    5. Provides citations for transparency

The result is a secure, explainable policy search assistant.

🏗️ System Architecture

User Question
      ↓
Streamlit UI
      ↓
Query Embedding (OpenAI)
      ↓
ChromaDB (Local Vector Store)
      ↓
Top-K Relevant Chunks Retrieved
      ↓
Prompt Construction
      ↓
GPT-4o-mini (Answer Generation)
      ↓
Final Answer with Citations

---
📂 Project Structure

genai-rag-policy-assistant/
│
├── Final_Project_RAG_SearchEngine.ipynb     # Main notebook (step-by-step RAG pipeline)
├── app.py                                   # Streamlit application
├── requirements.txt                         # Project dependencies
├── README.md                                # Project documentation
├── .env.example                             # Sample environment file
├── Policy documents/                        # Policy PDFs
│     └── XYZ_Dummy_Company_LTD_India_Employee_Policies.pdf
└── Project_Report.docx                      # Detailed academic report

---
⚙️ Installation & Setup
1️⃣ Clone the Repository
    1. Clone the repository: git clone <your-repo-link>
    2. Navigate to project folder:  cd "D:\Gen_AI\Final Project"

2️⃣ Install Dependencies:  pip install -r requirements.txt

3️⃣ Create Environment File: Create a .env file in the project root:  OPENAI_API_KEY=your_openai_api_key

---
▶️ Running the Project
## Option A — Notebook Version (Step-by-Step Execution)

1. Place your policy PDF (XYZ_Dummy_Company_LTD_India_Employee_Policies.pdf) inside: /Policy documents/
2. Ensure .env file contains your API key
3. Activate your Python environment
4. Launch Jupyter:  python -m jupyter notebook
5. Open: Final_Project_Sharif_Islam_RAG_SearchEngine.ipynb
6. Run all cells sequentially
7. Ask questions in the interactive prompt cell

Expected Output:
1. Generated answer
2. Source citations (document + page number)

## Option B — Streamlit Application (Recommended for Demo)
1. Ensure:
    * app.py exists
    *  Policy PDFs are in /Policy documents/
    *  .env file contains API key
    *   Dependencies are installed

2. From project directory: streamlit run app.py
3. Open browser at: http://localhost:8501
4. Enter question
5. Adjust Top-K slider if needed
6. Click Search

Expected Output:
  * Clean UI
  * Grounded answer
  * Source citations
  * Indexed chunk confirmation

🔎 Model & Parameter Choices
# Embedding Model: text-embedding-3-small
  * Cost-efficient
  * High semantic accuracy
  * Suitable for document search

# Chat Model: gpt-4o-mini
  * Fast
  * Affordable
  * Reliable for structured responses
  
# Chunking Strategy
   CHUNK_TOKENS = 700
   CHUNK_OVERLAP = 120
   TOP_K = 5
  Reasoning:
  * 700 tokens balances context richness and performance
  * 120 overlap prevents context loss
  * Top-K = 5 ensures answer quality without noise

🔐 Data Privacy
  * Policy PDFs remain local
  * Only embeddings and prompts are sent to OpenAI
  * ChromaDB runs locally
  * No external database is used

📊 Key Features

✔ Retrieval-Augmented Generation
✔ Source citations
✔ Local vector storage
✔ Cost-efficient LLM usage
✔ Interactive UI
✔ Modular architecture

👨‍💻 Author

Mohammad Sharif Islam
Advanced Certification in Generative AI (Batch 1)
📧 sharifislam.workmail@gmail.com
📞 9886431461
🔗 LinkedIn: https://www.linkedin.com/in/mohammad-sharif-islam-b6218714/ 




    




