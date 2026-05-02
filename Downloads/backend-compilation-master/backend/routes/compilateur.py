from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from services.compilateur import Compiler
from database.db import get_db

router = APIRouter(prefix="/nl", tags=["NLP"])

compiler = Compiler()

class NLRequest(BaseModel):
    phrase: str


# 🔹 NL → SQL + exécution avec SQLAlchemy
@router.post("/query")
def nl_to_sql(req: NLRequest, db: Session = Depends(get_db)):
    try:
        result = compiler.compile(req.phrase)

        if not result.success:
            return {"success": False, "error": result.error_message}

        result_sql = db.execute(text(result.sql))
        rows = result_sql.fetchall()
        cols = list(result_sql.keys())

        data = [dict(zip(cols, row)) for row in rows]

        return {
            "success": True,
            "sql": result.sql,
            "data": data
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# 🔹 Compile seulement
@router.post("/compile")
def compile_only(req: NLRequest):
    result = compiler.compile(req.phrase)

    return {
        "success": result.success,
        "sql": result.sql if result.success else None,
        "error": result.error_message
    }