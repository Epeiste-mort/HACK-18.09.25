from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.responses import HTMLResponse

from app.api.routes import router as api_router
from app.core.config import APP_VERSION
from app.logger import configure_logging, get_logger


configure_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="Anomaly Detection Service", version=APP_VERSION)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API
    app.include_router(api_router, prefix="/api")

    # Static (SPA)
    dist_path = Path("web") / "dist"
    if dist_path.exists():
        app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="spa")
    else:
        logger.warning("SPA not built: %s is missing", dist_path)

        @app.get("/", response_class=HTMLResponse)
        def fallback_page() -> str:
            # Минимальный интерфейс для загрузки файла
            return (
                "<!doctype html><html lang='ru'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
                "<title>Anomaly Detection AI</title>"
                "<style>*{margin:0;padding:0;box-sizing:border-box}"
                "body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;color:#fff;padding:20px}"
                ".wrap{max-width:800px;margin:0 auto}"
                "h1{font-size:42px;font-weight:800;margin:48px 0 12px;text-align:center;text-shadow:0 2px 20px rgba(0,0,0,0.3)}"
                ".subtitle{text-align:center;font-size:16px;opacity:0.95;margin-bottom:40px}"
                ".card{background:rgba(255,255,255,0.15);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.2);border-radius:24px;padding:40px;box-shadow:0 8px 32px rgba(0,0,0,0.2)}"
                ".upload-zone{border:3px dashed rgba(255,255,255,0.4);border-radius:16px;padding:48px 24px;text-align:center;cursor:pointer;transition:all 0.3s;margin-bottom:24px}"
                ".upload-zone:hover{border-color:#fff;background:rgba(255,255,255,0.08)}"
                ".upload-zone.dragging{border-color:#fbbf24;background:rgba(251,191,36,0.15)}"
                ".btn{background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);border:none;color:#fff;padding:14px 32px;border-radius:12px;font-size:16px;font-weight:600;cursor:pointer;transition:transform 0.2s,box-shadow 0.2s;box-shadow:0 4px 15px rgba(245,87,108,0.4)}"
                ".btn:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(245,87,108,0.6)}"
                ".btn:active{transform:translateY(0)}"
                ".result{margin-top:32px;padding:24px;background:rgba(255,255,255,0.1);border-radius:16px;backdrop-filter:blur(5px)}"
                ".result-label{font-size:28px;font-weight:700;margin-bottom:16px;text-align:center}"
                ".result-label.normal{color:#34d399}"
                ".result-label.pathology{color:#f87171}"
                ".prob{display:flex;justify-content:space-between;margin:12px 0;font-size:15px}"
                ".preview{text-align:center;margin-top:24px}"
                ".preview img{max-width:400px;border-radius:16px;box-shadow:0 8px 24px rgba(0,0,0,0.3);border:2px solid rgba(255,255,255,0.3)}"
                ".loading{text-align:center;font-size:18px;color:#fbbf24;animation:pulse 1.5s ease-in-out infinite}"
                "@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}"
                ".error{color:#fca5a5;margin-top:16px;padding:16px;background:rgba(220,38,38,0.2);border-radius:12px;border:1px solid rgba(220,38,38,0.4)}"
                "</style>"
                "</head><body><div class='wrap'><h1>🩺 Anomaly Detection AI</h1>"
                "<p class='subtitle'>Анализ рентгеновских снимков с помощью нейросети</p>"
                "<div class='card'><form id='f' enctype='multipart/form-data'>"
                "<div class='upload-zone' id='zone'><input type='file' name='file' id='file' style='display:none' accept='.zip,.tar,.gz,.nii,.dcm'/>"
                "<div style='font-size:48px;margin-bottom:16px'>📁</div>"
                "<div style='font-size:18px;font-weight:600;margin-bottom:8px'>Перетащите файл сюда</div>"
                "<div style='opacity:0.8;font-size:14px'>или нажмите для выбора</div>"
                "<div style='opacity:0.7;font-size:13px;margin-top:12px'>Поддержка: .zip, .tar.gz, .nii, .dcm</div></div>"
                "<div style='text-align:center'><button class='btn' type='submit'>🔬 Начать анализ</button></div>"
                "</form><div id='result'></div></div></div><script>"
                "const f=document.getElementById('f'),zone=document.getElementById('zone'),file=document.getElementById('file'),result=document.getElementById('result');"
                "zone.onclick=()=>file.click();"
                "file.onchange=()=>{if(file.files[0])zone.querySelector('div:nth-child(2)').textContent='Файл: '+file.files[0].name};"
                "['dragenter','dragover'].forEach(e=>zone.addEventListener(e,ev=>{ev.preventDefault();zone.classList.add('dragging')}));"
                "['dragleave','drop'].forEach(e=>zone.addEventListener(e,()=>zone.classList.remove('dragging')));"
                "zone.addEventListener('drop',e=>{e.preventDefault();file.files=e.dataTransfer.files;file.onchange()});"
                "f.addEventListener('submit',async e=>{e.preventDefault();result.innerHTML='<div class=\"loading\">⏳ Обработка данных...</div>';"
                "const fd=new FormData(f);try{const r=await fetch('/api/analyze',{method:'POST',body:fd});"
                "if(!r.ok){result.innerHTML='<div class=\"error\">Ошибка: '+(await r.text())+'</div>';return;}"
                "const j=await r.json();"
                "const labelClass=j.label==='Норма'?'normal':'pathology';"
                "result.innerHTML='<div class=\"result\"><div class=\"result-label '+labelClass+'\">'+j.label+'</div>'"
                "+'<div class=\"prob\"><span>Норма:</span><strong>'+(j.probabilities[0]*100).toFixed(1)+'%</strong></div>'"
                "+'<div class=\"prob\"><span>Патология:</span><strong>'+(j.probabilities[1]*100).toFixed(1)+'%</strong></div>'"
                "+'<div class=\"prob\"><span>Устройство:</span><strong>'+j.device+'</strong></div>'"
                "+(j.preview_png_b64?'<div class=\"preview\"><img src=\"data:image/png;base64,'+j.preview_png_b64+'\"/></div>':'')+'</div>';"
                "}catch(err){result.innerHTML='<div class=\"error\">'+String(err)+'</div>';}});"
                "</script></body></html>"
            )

    return app


app = create_app()


