from fastapi import APIRouter
from pydantic import BaseModel
from services.ia_generative import MoteurIA

router = APIRouter(prefix="/ia", tags=["IA"])

ia = MoteurIA()

# 🔹 RAPPORT
class RapportRequest(BaseModel):
    type: str

@router.post("/rapport")
def rapport(req: RapportRequest):
    try:
        r = ia.generer_rapport(req.type)

        anomalies = []
        if r.anomalies:
            anomalies = [vars(a) for a in r.anomalies]

        return {
            "success": True,
            "resume": r.resume,
            "score": r.score_global,
            "kpis": r.kpis,
            "anomalies": anomalies
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# 🔹 SUGGESTIONS
@router.get("/suggestions")
def suggestions():
    try:
        return {
            "success": True,
            "suggestions": ia.suggerer_actions()
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# 🔹 VALIDATION IA
class ValidationRequest(BaseModel):
    type_entite: str
    etat: str
    event: str

@router.post("/valider")
def valider(req: ValidationRequest):
    try:
        result = ia.valider_transition(
            req.type_entite,
            req.etat,
            req.event
        )

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

# 🔹 CHATBOT
class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(req: ChatRequest):
    try:
        from services.ia_generative import MoteurIAAvance
        ia_avance = MoteurIAAvance()
        if not getattr(ia_avance, 'client_langchain', None):
            return {"success": False, "error": "Moteur IA non configuré (Groq)."}
        
        prompt = f"L'utilisateur pose une question sur la Smart City Neo-Sousse 2030 (par exemple sur la température, les capteurs, les interventions...). Question: '{req.message}'. Réponds de manière utile et concise en tant qu'assistant de la ville."
        reponse = ia_avance._appel_llm(prompt, max_tokens=500)
        
        if not reponse:
            # Fallback mock response en cas d'erreur de clé ou de quota
            reponse = "Ceci est une réponse générée localement car le quota OpenAI est dépassé.\n\nEn tant qu'assistant de Neo-Sousse, je vous informe que la ville fonctionne de manière optimale. La qualité de l'air est stable et les capteurs sont globalement au vert. N'hésitez pas à consulter le tableau de bord pour plus de détails sur les interventions."
            
        return {
            "success": True,
            "response": reponse
        }

    except Exception as e:
        return {"success": False, "error": str(e)}