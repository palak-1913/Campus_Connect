# 🎓 Campus Connect — Skill-Based Student Recommendation System

> A semantic NLP system that recommends the most relevant student peers based on skill profiles, academic performance, and domain interests — built using Sentence Transformers and Cosine Similarity.

---

## 📌 Overview

Academic institutions generate rich student profile data — skills, projects, CGPA, and domain interests — but rarely leverage it intelligently. **Campus Connect** bridges that gap by building a smart recommendation engine that surfaces the most compatible peers for collaboration, mentorship, or career guidance.

This project compares two approaches:
- **Baseline:** TF-IDF Vectorization + K-Means Clustering
- **Final Model:** Sentence Transformer Embeddings (`all-MiniLM-L6-v2`) + Hybrid Cosine Similarity Scoring

The Sentence Transformer approach significantly outperformed TF-IDF, especially in capturing **cross-domain semantic relationships** (e.g., recognising that *Deep Learning* and *Machine Learning* are related skills).

---

## 🧭 Development Journey — What Actually Happened

Building this project wasn't straightforward. Here's the honest story of the challenges we hit and how we solved them.

### 📦 Challenge 1: Data Generation — "All at Once" Didn't Work

Our first attempt was to generate the entire dataset of 1,000 students in one go — randomly assigning skills, domains, and projects all together.

**The problem?** The data was incoherent. A student tagged under *Data Analytics* might have skills like `game development` or `mobile UI design` — because the random sampling had no domain awareness. The dataset looked complete on the surface but was effectively noise.

**The fix:** We scrapped that approach and rebuilt the pipeline **domain by domain**:

```
Generate Data Analytics students   →  ~200 records (only DA skills & projects)
Generate AI students               →  ~200 records (only AI skills & projects)
Generate Web Dev students          →  ~200 records (only Web skills & projects)
... and so on for each domain
        ↓
Merge all 5 domain datasets into one DataFrame
        ↓
Shuffle with random_state=42 (for reproducibility)
        ↓
Assign sequential IDs post-shuffle
```

This ensured every student profile was **internally consistent** — skills, projects, and domain interests all aligned — while the final merged dataset had enough diversity for meaningful recommendations.

---

### 🔤 Challenge 2: TF-IDF Missed the Meaning — Sentence Transformers Saved It

Once the data was clean, we built the first recommendation model using **TF-IDF vectorization + K-Means clustering**. It seemed reasonable — convert skills to vectors, cluster similar students, recommend from the same cluster.

**The problem?** TF-IDF treats every word as an independent token. It had no understanding that:

> `"machine learning"` and `"ML"` are the same thing  
> `"deep learning"` and `"neural networks"` are closely related  
> `"data analysis"` and `"EDA"` mean the same concept  

So students with highly overlapping skills were being placed in **completely different clusters** just because they used slightly different terminology. The elbow method showed no clear optimal cluster count, and silhouette scores stayed between 0.08–0.14 — barely above random.

**The fix:** We switched to **Sentence Transformers** (`all-MiniLM-L6-v2`), a pre-trained model that converts text into 384-dimensional semantic embeddings. Instead of matching exact words, it understands *meaning*.

```
TF-IDF:   "ML" ≠ "Machine Learning"   ← treated as completely different tokens
SBERT:    "ML" ≈ "Machine Learning"   ← recognised as semantically identical
```

Cross-domain recommendations immediately made sense. An AI student skilled in *Deep Learning and NLP* started appearing in recommendations for Data Analytics students — correctly — because the embeddings understood the semantic overlap.

---



- 🔤 **Semantic Skill Matching** using `all-MiniLM-L6-v2` (384-dim dense embeddings)
- 📊 **Hybrid Scoring** combining cosine similarity (80%), project count (12%), and CGPA (8%)
- 🛠️ **Baseline Comparison** — documents why TF-IDF fails for semantic skill tasks
- 🧪 **Synthetic Dataset** of 1,000 student records across 5 academic domains
- 📈 **EDA Visualisations** — CGPA distribution, domain bar charts, skill word clouds, cosine similarity heatmaps
- 🌐 **Web Interface** built with HTML/CSS/JS + Flask backend

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| NLP / Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) |
| Baseline ML | `scikit-learn` (TF-IDF, K-Means, Silhouette) |
| Data Handling | `pandas`, `NumPy` |
| Visualisation | `matplotlib`, `seaborn`, `wordcloud` |
| Backend | Flask (`app.py`) |
| Frontend | HTML, CSS, JavaScript |

---

## 📁 Project Structure

```
Campus_Connect/
│
├── data/                          # All datasets
│   ├── final_clean_dataset.csv    # Cleaned, merged synthetic dataset (1000 records)
│   ├── final_data.csv             # Raw merged data (pre-cleaning)
│   ├── data_science_dataset.csv
│   ├── ml_engineer_dataset.csv
│   ├── agentic_ai_dataset.csv
│   ├── ai_genai_dataset.csv
│   ├── big_data_engineer_dataset.csv
│   ├── cloud_engineer_dataset.csv
│   ├── backend_engineer_dataset.csv
│   ├── frontend_students.csv
│   ├── fullstack_students.csv
│   ├── game_dev_dataset.csv
│   ├── mobile_app_dataset.csv
│   ├── product_analytics_dataset.csv
│   ├── software_dev_students.csv
│   └── software_quality_dataset.csv
│
├── static/                        # Frontend assets
│   ├── index.html                 # Landing page
│   ├── peer.html                  # Peer recommendation UI
│   ├── project.html               # Project recommendation UI
│   ├── documentation.html         # System documentation page
│   ├── app.js                     # Frontend logic
│   ├── project.js                 # Project page logic
│   └── style.css                  # Stylesheet
│
├── CodeBook.ipynb                 # Main notebook: EDA, modelling, evaluation
├── syntheticdata.ipynb            # Synthetic data generation pipeline
├── app.py                         # Flask backend / API server
├── requirements.txt               # Python dependencies
└── README.md
```

---

## 📊 Dataset

Since real student data was unavailable due to institutional privacy policies, a **synthetic dataset** of **1,000 student records** was generated programmatically across 5 academic domains:

| Domain | Records |
|---|---|
| Data Analytics | ~200 |
| Artificial Intelligence | ~200 |
| Web Development | ~200 |
| Cybersecurity | ~200 |
| Cloud Computing | ~200 |

**Schema:**

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Unique student identifier |
| `Name` | String | Student name (anonymised) |
| `Course` | String | Enrolled programme |
| `Skills` | String | Pipe-separated technical skills |
| `CGPA` | Float | GPA on 10-point scale (5.0–10.0) |
| `Interested_domain` | String | Primary domain of interest |
| `Projects` | String | Pipe-separated project titles |
| `Number of Projects` | Integer | Total projects (0–10) |
| `Semester` | Integer | Current semester (1–8) |

---

## ⚙️ How It Works

### Pipeline

```
Student Profiles (CSV)
        ↓
Preprocessing (lowercase, null fill, feature concat)
        ↓
Embedding: all-MiniLM-L6-v2  →  384-dim vector per student
        ↓
Cosine Similarity Matrix
        ↓
Hybrid Score = 0.80 × Cosine Sim
             + 0.12 × Normalised Project Count
             + 0.08 × Normalised CGPA
        ↓
Top-N Ranked Recommendations
```

### Scoring Formula

```python
score = (0.80 * cosine_similarity) + 
        (0.12 * (num_projects / 10)) + 
        (0.08 * normalized_cgpa)
```

---

## 📉 Why TF-IDF Failed (and What We Learned)

The baseline TF-IDF + K-Means approach was tested first. Here's what happened:

| Metric | TF-IDF + K-Means | Sentence Transformer |
|---|---|---|
| Semantic Capture | ❌ Poor | ✅ Excellent |
| Silhouette Score | 0.08 – 0.14 | N/A (similarity-based) |
| Cross-domain Accuracy | ❌ Inaccurate | ✅ Contextually Relevant |
| Cold-start Handling | Limited | Effective |

The elbow method produced no clear inflection point and silhouette scores stayed low (0.08–0.14) — confirming that TF-IDF's bag-of-words representation couldn't capture that *"neural networks"* and *"deep learning"* are related skills. This failure is documented in `CodeBook.ipynb`.

---

## 🔍 Sample Output

Query: **Student ID 42** (Data Analytics)

| Rank | Student | Domain | Skills | Score |
|---|---|---|---|---|
| 1 | Aryan Sharma | Data Analytics | Python, Pandas, Data Viz | 0.923 |
| 2 | Priya Verma | Data Analytics | SQL, ML, EDA | 0.911 |
| 3 | Rahul Mishra | **Artificial Intelligence** | Deep Learning, NLP, Python | 0.887 |
| 4 | Sneha Gupta | Data Analytics | Statistics, Tableau, R | 0.874 |
| 5 | Amit Rawat | Data Analytics | ML, Feature Engineering | 0.861 |

> Rank 3 correctly surfaces an AI student whose skills are **semantically adjacent** to Data Analytics — something TF-IDF entirely missed.

---

## 🛠️ Setup & Installation

```bash
# Clone the repository
git clone https://github.com/nikhil1913/Campus_Connect.git
cd Campus_Connect

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
```

Then open `http://localhost:5000` in your browser.

---

## 📦 Requirements

Key packages from `requirements.txt`:

```
sentence-transformers
scikit-learn
pandas
numpy
matplotlib
seaborn
wordcloud
flask
```

---

## 🔮 Future Scope

- 🏫 **Real Data Integration** — replace synthetic data with anonymised institutional records
- 🕸️ **Graph Neural Networks** — model student-skill relationships as a knowledge graph
- 🌐 **REST API Deployment** — expose recommendation engine for integration with university portals
- 🔒 **Federated Learning** — enable privacy-preserving cross-institution model training
- 📐 **Formal Evaluation** — precision, recall, NDCG metrics with domain expert validation

---

## 👤 Author

**Nikhil Singh Bisht**  
*Linkiden* - www.linkedin.com/in/nikhibisht00 -
*medium* - https://medium.com/@nikhilbisht226
---

## 📄 License

This project is for academic purposes. Dataset is fully synthetic.
