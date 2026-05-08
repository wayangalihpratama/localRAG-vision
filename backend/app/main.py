from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LocalRAG Vision API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "LocalRAG Vision API is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
