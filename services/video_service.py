from utils.db import get_db_connection
from fastapi import HTTPException


def search_videos(q=None, course_id=None, prof=None, limit=20, offset=0):
    """
    Search videos using JOINs across:
    - Videos
    - CourseOfferings
    - Courses
    - CourseInstructors

    Adds item-level HATEOAS linked data:
    - self link  -> /videos/<video_id>
    - course link -> /courses/<course_id>
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ---- BASE QUERY ----
        query = """
            SELECT 
                v.video_id,
                v.title,
                v.gcs_path,
                v.uploaded_at,
                co.course_id,
                c.course_name,
                v.prof_uni
            FROM Videos v
            JOIN CourseOfferings co ON v.offering_id = co.offering_id
            JOIN Courses c ON co.course_id = c.course_id
            JOIN CourseInstructors ci 
                ON ci.offering_id = co.offering_id
                AND ci.prof_uni = v.prof_uni
            WHERE 1=1
        """

        params = []

        # ---- KEYWORD FILTER ----
        if q:
            query += " AND v.title LIKE %s"
            params.append(f"%{q}%")

        # ---- COURSE FILTER ----
        if course_id:
            query += " AND co.course_id = %s"
            params.append(course_id)

        # ---- PROFESSOR UNI FILTER ----
        if prof:
            query += " AND ci.prof_uni = %s"
            params.append(prof)

        # ---- SORT + PAGINATION ----
        query += " ORDER BY v.uploaded_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # ---- Add item-level HATEOAS links ----
        for item in rows:
            item["links"] = [
                {"rel": "self", "href": f"/videos/{item['video_id']}"},
                {"rel": "course", "href": f"/courses/{item['course_id']}"}
            ]

        # ---- Collection-level response ----
        return {
            "items": rows,
            "page_size": limit,
            "offset": offset,
            "links": [
                {"rel": "self", "href": f"/videos?limit={limit}&offset={offset}"}
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


def add_videodata(video_id: str = None, offering_id: int = None, prof_uni: str = None, title: str = None, gcs_path: str = None):
    """
    Add video metadata:
    
    """
    insert_query = """
        INSERT INTO Videos (video_id, offering_id, prof_uni, title, gcs_path)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    # 2. Create a tuple of data in the exact order of the columns
    data_tuple = (video_id, offering_id, prof_uni, title, gcs_path)
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(insert_query, data_tuple)
        
        # 4. CRITICAL: Commit the transaction to save the data
        conn.commit()

        # 5. Clean up
        cursor.close()
        conn.close()

        return {
            "message": "Video metadata added successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")
