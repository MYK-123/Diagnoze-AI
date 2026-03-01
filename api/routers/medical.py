from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Any, Optional

from ..auth_db import get_current_user
from ..models.responses import success_response

# Import core modules
from core.disease import get_all_diseases_cache
from core.symptoms import get_all_symptoms_cache
from core.disease_symptoms_relation import get_relations_cache
from content.educational_content import get_all_education_content_cache

router = APIRouter()

@router.get("/symptoms", summary="Get symptoms list")
async def get_symptoms(
    q: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = Query(None, description="Filter by category"),
    user: dict[str, Any] = Depends(get_current_user)
):
    """Get list of symptoms from core database"""
    try:
        symptoms_obj = get_all_symptoms_cache()
        all_symptoms = symptoms_obj.get_all_list()
        
        # Filter by search term
        filtered_symptoms = all_symptoms
        if q:
            filtered_symptoms = [
                s for s in filtered_symptoms
                if q.lower() in s.get_name().lower()
            ]
        
        # Filter by category
        if category:
            filtered_symptoms = [
                s for s in filtered_symptoms
                if s.get_category().lower() == category.lower()
            ]
        
        # Extract categories
        categories = {s.get_category() for s in all_symptoms if s.get_category()}
        
        # Format response
        symptoms_list: list[dict[str, Any]] = [
            {
                "id": s.get_id(),
                "name": s.get_name(),
                "category": s.get_category()
            }
            for s in filtered_symptoms
        ]
        
        return success_response({
            "symptoms": symptoms_list,
            "total": len(filtered_symptoms),
            "categories": sorted(list(categories))
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving symptoms: {str(e)}")

@router.get("/symptoms/{symptom_id}", summary="Get symptom details")
async def get_symptom(symptom_id: int, user: dict[str, Any] = Depends(get_current_user)):
    """Get detailed symptom information"""
    try:
        symptoms_obj = get_all_symptoms_cache()
        symptom = symptoms_obj.filter_by_id(symptom_id).get_all_list()
        
        if not symptom:
            raise HTTPException(status_code=404, detail="Symptom not found")
        
        s = symptom[0]
        return success_response({
            "id": s.get_id(),
            "name": s.get_name(),
            "category": s.get_category()
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving symptom: {str(e)}")

@router.get("/diseases", summary="Get diseases list")
async def get_diseases(
    q: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = Query(None, description="Filter by category"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    user: dict[str, Any] = Depends(get_current_user)
):
    """Get list of diseases from core database"""
    try:
        diseases_obj = get_all_diseases_cache()
        all_diseases = diseases_obj.get_all_diseases_list()
        
        # Filter by search term
        filtered_diseases = all_diseases
        if q:
            filtered_diseases = [
                d for d in filtered_diseases
                if q.lower() in d.get_disease_name().lower()
            ]
        
        # Filter by category
        if category:
            filtered_diseases = [
                d for d in filtered_diseases
                if d.get_category().lower() == category.lower()
            ]
        
        # Filter by severity
        if severity:
            filtered_diseases = [
                d for d in filtered_diseases
                if d.get_severity_level_str().lower() == severity.lower()
            ]
        
        # Extract categories and severity levels
        categories = {d.get_category() for d in all_diseases if d.get_category()}
        severity_levels = {d.get_severity_level_str() for d in all_diseases}
        
        # Format response
        diseases_list: list[dict[str, Any]] = [
            {
                "id": d.get_disease_id(),
                "name": d.get_disease_name(),
                "category": d.get_category(),
                "severity": d.get_severity_level_str()
            }
            for d in filtered_diseases
        ]
        
        return success_response({
            "diseases": diseases_list,
            "total": len(filtered_diseases),
            "categories": sorted(list(categories)),
            "severity_levels": sorted(list(severity_levels))
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving diseases: {str(e)}")

@router.get("/diseases/{disease_id}", summary="Get disease details")
async def get_disease(disease_id: int, user: dict[str, Any] = Depends(get_current_user)):
    """Get detailed disease information"""
    try:
        diseases_obj = get_all_diseases_cache()
        disease = diseases_obj.filter_by_id(disease_id).get_all_diseases_list()
        
        if not disease:
            raise HTTPException(status_code=404, detail="Disease not found")
        
        d = disease[0]
        
        # Get related symptoms from disease_symptoms relation
        relations_obj = get_relations_cache()
        all_relations = relations_obj.get_all_relation_list()
        symptom_ids = [rel.get_symptom_id() for rel in all_relations if rel.get_disease_id() == d.get_disease_id()]
        
        symptoms_obj = get_all_symptoms_cache()
        related_symptoms: list[dict[str, Any]] = [
            {
                "id": s.get_id(),
                "name": s.get_name(),
                "category": s.get_category()
            }
            for s in symptoms_obj.get_all_list()
            if s.get_id() in symptom_ids
        ]
        
        return success_response({
            "id": d.get_disease_id(),
            "name": d.get_disease_name(),
            "category": d.get_category(),
            "severity": d.get_severity_level_str(),
            "symptoms": related_symptoms
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving disease: {str(e)}")

@router.get("/search", summary="Search medical information")
async def search_medical(
    q: str = Query(..., description="Search query"),
    type: Optional[str] = Query(None, description="Type: symptoms, diseases, or all"),
    limit: int = Query(10, ge=1, le=50),
    user: dict[str, Any] = Depends(get_current_user)
):
    """Search for symptoms and diseases"""
    try:
        query_lower = q.lower()
        symptoms: list[dict[str, Any]] = []
        diseases: list[dict[str, Any]] = []
        
        # Search symptoms
        if type in [None, "all", "symptoms"]:
            symptoms_obj = get_all_symptoms_cache()
            symptoms = [
                {
                    "id": s.get_id(),
                    "name": s.get_name(),
                    "category": s.get_category(),
                    "type": "symptom"
                }
                for s in symptoms_obj.get_all_list()
                if query_lower in s.get_name().lower()
            ][:limit]
        
        # Search diseases
        if type in [None, "all", "diseases"]:
            diseases_obj = get_all_diseases_cache()
            diseases = [
                {
                    "id": d.get_disease_id(),
                    "name": d.get_disease_name(),
                    "category": d.get_category(),
                    "severity": d.get_severity_level_str(),
                    "type": "disease"
                }
                for d in diseases_obj.get_all_diseases_list()
                if query_lower in d.get_disease_name().lower()
            ][:limit]
        
        return success_response({
            "symptoms": symptoms,
            "diseases": diseases,
            "total": len(symptoms) + len(diseases)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching medical data: {str(e)}")

@router.get("/educational/{disease_id}", summary="Get educational content")
async def get_educational_content(disease_id: int, user: dict[str, Any] = Depends(get_current_user)):
    """Get educational content for disease"""
    try:
        diseases_obj = get_all_diseases_cache()
        disease = diseases_obj.filter_by_id(disease_id).get_all_diseases_list()
        
        if not disease:
            raise HTTPException(status_code=404, detail="Disease not found")
        
        d = disease[0]
        
        # Get educational content
        content_obj = get_all_education_content_cache()
        content_list = content_obj.filter_by_disease_id(disease_id).get_all_list()
        
        if not content_list:
            # Return basic info if no educational content available
            return success_response({
                "disease_id": disease_id,
                "disease_name": d.get_disease_name(),
                "sections": [
                    {
                        "title": f"About {d.get_disease_name()}",
                        "content": f"{d.get_disease_name()} is a medical condition in the {d.get_category()} category with {d.get_severity_level_str()} severity.",
                    }
                ],
                "references": ["Diagnoze AI Medical Database"]
            })
        
        # Format educational content
        sections: list[dict[str, Any]] = [
            {
                "title": c.get_title(),
                "content": c.get_content_text(),
                "verified": c.get_is_verified()
            }
            for c in content_list
        ]
        
        return success_response({
            "disease_id": disease_id,
            "disease_name": d.get_disease_name(),
            "sections": sections,
            "references": ["Diagnoze AI Medical Database"]
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving educational content: {str(e)}")

