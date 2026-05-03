from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import WebSocket, WebSocketDisconnect
from websocket.manager import manager
import threading
from database.listener import start_listener
from routes.ia_pdf_route import router as ia_pdf_router

from routes import *   # 🔥 UNE SEULE LIGNE (important)

from database.db import get_db
from database.init_db import init_db

import models  # 🔥 important pour create tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # 🔥 lancer listener PostgreSQL
    thread = threading.Thread(target=start_listener, daemon=True)
    thread.start()
    yield

app = FastAPI(
    title=" Smart City Tunisia API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB INIT
# (L'initialisation de la DB est maintenant gérée par lifespan au-dessus)

# ROUTERS (propre)
app.include_router(zone_router)
app.include_router(capteur_router)
app.include_router(mesure_router)
app.include_router(citoyen_router)
app.include_router(technicien_router)
app.include_router(proprietaire_router)
app.include_router(intervention_router)
app.include_router(consultation_router)
app.include_router(vehicule_router)
app.include_router(trajet_router)
app.include_router(nl_router)
app.include_router(auto_router)
app.include_router(ia_router)
app.include_router(kpis_router)
app.include_router(ia_pdf_router)

# ROOT
@app.get("/")
def root():
    return {"status": "online"}

# HEALTH
@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except:
        return {"status": "error", "database": "down"}
    

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()  # garde connexion vivante
    except WebSocketDisconnect:
        manager.disconnect(websocket)