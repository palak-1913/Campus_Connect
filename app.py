from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn
import math

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variables for data and model
data_sent = pd.DataFrame()
embeddings = None
model = None

def load_and_preprocess_data():
    global data_sent, embeddings, model
    print("Loading model and data...")
    # Load model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Load data
    raw_data = pd.read_csv('final_data.csv')
    raw_data = raw_data.sample(frac=1, random_state=42).reset_index(drop=True)
    raw_data['id'] = range(1, len(raw_data) + 1)
    
    # Select columns based on notebook execution
    raw_data.columns = ['Name','Course','Skills','CGPA','Interested_domain','Projects','Number of Projects','Semester','id']
    raw_data = raw_data[['id','Name', 'Number of Projects', 'Semester' ,'CGPA', 'Course', 'Skills', 'Interested_domain', 'Projects']]
    raw_data.fillna('No projects', inplace=True)
    
    for i in raw_data.columns:
        if raw_data[i].dtype == 'object':
            raw_data[i] = raw_data[i].str.lower()
            
    data_sent = raw_data.copy()
    data_sent['text'] = data_sent['Skills'] + " " + data_sent['Projects']
    
    print("Generating embeddings (this may take a moment)...")
    embeddings = model.encode(data_sent['text'].tolist(), show_progress_bar=False)
    
    data_sent['proj_norm'] = (data_sent['Number of Projects'] - data_sent['Number of Projects'].min()) / (
        data_sent['Number of Projects'].max() - data_sent['Number of Projects'].min() + 1e-8
    )

    data_sent['cgpa_norm'] = (data_sent['CGPA'] - data_sent['CGPA'].min()) / (
        data_sent['CGPA'].max() - data_sent['CGPA'].min() + 1e-8
    )
    print("Startup complete!")

@app.on_event("startup")
async def startup_event():
    load_and_preprocess_data()

class RecommendRequest(BaseModel):
    student_id: int
    top_n: int = 10

class ProjectRecommendRequest(BaseModel):
    skills_req: str
    project_title: str
    top_n: int = 10

@app.get("/")
def read_root():
    return FileResponse("static/index.html")
    
@app.get("/peer")
def read_peer():
    return FileResponse("static/peer.html")

@app.get("/project")
def read_project():
    return FileResponse("static/project.html")

@app.get("/documentation")
def read_doc():
    return FileResponse("static/documentation.html")
@app.post("/api/recommend")
def recommend(req: RecommendRequest):
    student_id = req.student_id
    top_n = req.top_n
    
    if student_id not in data_sent['id'].values:
        raise HTTPException(status_code=404, detail="Student ID not found. Max ID is " + str(len(data_sent)))
        
    df = data_sent.reset_index(drop=True)
    
    # Get index for the given student_id
    target_idx = df.index[df['id'] == student_id].tolist()[0]
    target_vec = embeddings[target_idx]
    
    # similarity
    sim_scores = cosine_similarity([target_vec], embeddings).flatten()

    # scoring
    final_scores = (
        0.80 * sim_scores +
        0.12 * df['proj_norm'].values +
        0.08 * df['cgpa_norm'].values
    )

    top_indices = np.argsort(final_scores)[::-1]
    
    # Filter out the student itself from recommendations
    filtered_indices = [idx for idx in top_indices if idx != target_idx][:top_n]

    results = df.iloc[filtered_indices].copy()
    results['score'] = final_scores[filtered_indices]
    
    target_res = df.iloc[[target_idx]].copy()
    target_res['score'] = 1.0

    # Capitalize for display
    for df_to_process in [results, target_res]:
        df_to_process['Name'] = df_to_process['Name'].str.title()
        df_to_process['Interested_domain'] = df_to_process['Interested_domain'].str.title()
        df_to_process['Course'] = df_to_process['Course'].str.upper()
    
    results = results[['id', 'Name','Interested_domain', 'Course', 'Skills','Projects','CGPA','score']]
    target_res = target_res[['id', 'Name','Interested_domain', 'Course', 'Skills','Projects','CGPA','score']]
    
    results = results.replace({np.nan: None})
    target_res = target_res.replace({np.nan: None})
    
    return {
        "target": target_res.to_dict(orient="records")[0],
        "recommendations": results.to_dict(orient="records")
    }

@app.post("/api/recommend_project")
def recommend_project(req: ProjectRecommendRequest):
    skills_req = req.skills_req
    project_title = req.project_title
    top_n = req.top_n
    
    query_text = skills_req + " " + project_title
    df = data_sent.reset_index(drop=True)
    
    target_vec = model.encode([query_text], show_progress_bar=False)[0]
    
    sim_scores = cosine_similarity([target_vec], embeddings).flatten()

    final_scores = (
        0.80 * sim_scores +
        0.12 * df['proj_norm'].values +
        0.08 * df['cgpa_norm'].values
    )

    # Make sure we don't exceed length
    top_n = min(top_n, len(df))
    top_indices = np.argsort(final_scores)[::-1][:top_n]

    results = df.iloc[top_indices].copy()
    results['score'] = final_scores[top_indices]

    results['Name'] = results['Name'].str.title()
    results['Interested_domain'] = results['Interested_domain'].str.title()
    results['Course'] = results['Course'].str.upper()

    results = results[['id', 'Name','Interested_domain', 'Course', 'Skills','Projects','CGPA','score']]
    results = results.replace({np.nan: None})

    return results.to_dict(orient="records")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
