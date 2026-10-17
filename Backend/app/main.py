from fastapi import FastAPI

app = FastAPI(title="SachCheck Backend")


@app.get("/health")
def health():
    return {"status": "ok", "project": "SachCheck"}
