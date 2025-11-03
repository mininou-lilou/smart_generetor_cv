# app/main.py
# --- STANDARD LIBRARY ---
from datetime import datetime
import tempfile
from pathlib import Path

# --- THIRD PARTY ---
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from weasyprint import HTML

app = FastAPI(title="Smart CV Generator")

# Configuration templates & static
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Modèle de données typé
class CVData(BaseModel):
    name: str
    email: str
    skills: str
    experience: str


@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request) -> HTMLResponse:
    """Affiche la page du formulaire."""
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/generate")
async def generate_pdf(
    _: Request,
    name: str = Form(...),
    email: str = Form(...),
    skills: str = Form(...),
    experience: str = Form(...),
) -> FileResponse:
    """Génère un PDF à partir des données du formulaire."""
    data = CVData(name=name, email=email, skills=skills, experience=experience)

    html_content: str = templates.get_template("cv_template.html").render(
        cv=data.dict(), year=datetime.now().year
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        pdf_path: Path = Path(tmp_pdf.name)

    return FileResponse(
        path=pdf_path,
        filename=f"{data.name.replace(' ', '_')}_CV.pdf",
        media_type="application/pdf",
    )
