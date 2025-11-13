'''from utils.db import get_db_connection
from fastapi import HTTPException

def search_videos(q=None, offering_id=None, prof=None, limit=20, offset=0):
    """
    Directly queries the Videos DB.
    Used internally by Search and Upload microservices.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Videos WHERE 1=1"
        params = []

        # Filters
        if q:
            query += " AND title LIKE %s"
            params.append(f"%{q}%")
        if offering_id:
            query += " AND offering_id = %s"
            params.append(offering_id)
        if prof:
            query += " AND prof_uni LIKE %s"
            params.append(f"%{prof}%")

        query += " ORDER BY uploaded_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return {
            "items": rows,
            "page_size": limit,
            "offset": offset,
            "links": [
                {"rel": "self", "href": f"/videos?q={q or ''}&limit={limit}&offset={offset}"}
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")'''


# services/video_service.py
def search_videos(q=None, offering_id=None, prof=None, limit=20, offset=0):
    """
    Temporary mock version — just confirms that the call reached the service.
    """
    print(f"[DEBUG] Received call in videos_composite_microservice")
    print(f"[DEBUG] Params: q={q}, offering_id={offering_id}, prof={prof}, limit={limit}, offset={offset}")

    # Simulate response for testing integration
    return {
        "message": "Received call from Search microservice",
        "params": {
            "q": q,
            "offering_id": offering_id,
            "prof": prof,
            "limit": limit,
            "offset": offset
        },
        "items": [],
        "page_size": limit,
        "offset": offset,
        "links": [
            {"rel": "self", "href": f"/videos?q={q or ''}&limit={limit}&offset={offset}"}
        ]
    }

