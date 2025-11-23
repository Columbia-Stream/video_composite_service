from utils.db import get_db_connection
from fastapi import HTTPException


def search_videos(q=None, course_id=None, prof=None, limit=20, offset=0):
    """
    Search videos using JOINs across:
    - Videos
    - CourseOfferings
    - Courses
    - CourseInstructors
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

        # ---- Final response ----
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


# -----------------------------------------------------------
# Insert video metadata
# -----------------------------------------------------------
def add_videodata(video_id: str = None, offering_id: int = None,
                  prof_uni: str = None, title: str = None, gcs_path: str = None):
    """
    Add video metadata into Videos table.
    """

    insert_query = """
        INSERT INTO Videos (video_id, offering_id, prof_uni, title, gcs_path)
        VALUES (%s, %s, %s, %s, %s)
    """

    data_tuple = (video_id, offering_id, prof_uni, title, gcs_path)

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(insert_query, data_tuple)
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "Video metadata added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

# -----------------------------------------------------------
# Get professor by offeringID
# -----------------------------------------------------------

def get_instructors_by_offering(offering_id: int):
    """
    Retrieves all attributes (columns) from the CourseInstructors table 
    for a specific offering_id.
    
    Args:
        offering_id: The ID of the course offering (input parameter).
        
    Returns:
        A list of dictionaries, where each dictionary represents a row 
        (e.g., {'prof_uni': 'ts3747'}).
    """
    
    # 1. SQL Query using %s placeholder (required for mysql-connector)
    query = """
        SELECT * FROM CourseInstructors 
        WHERE offering_id = %s
    """
    
    # 2. Data parameter tuple
    data_tuple = (offering_id,) # CRITICAL: Must be a tuple, even with one element

    try:
        # Use the context manager to automatically close the connection
        with get_db_connection() as conn:
            # Use dictionary=True to get results as dicts instead of tuples
            cursor = conn.cursor(dictionary=True) 

            cursor.execute(query, data_tuple)
            
            # Fetch all rows that match the query
            rows = cursor.fetchall()

            # The connection and cursor are closed automatically by the 'with' block

            return rows

    except Exception as e:
        # Re-raise the error as an HTTPException for the API layer to handle
        raise HTTPException(status_code=500, detail=f"DB error retrieving instructors: {str(e)}")

# -----------------------------------------------------------
# Insert offering_id and professor association 
# -----------------------------------------------------------
def add_association(offering_id: int = None, prof_uni: str = None):
   

    insert_query = """
        INSERT INTO CourseInstructors (offering_id, prof_uni)
        VALUES (%s, %s)
    """

    data_tuple = (offering_id, prof_uni)

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(insert_query, data_tuple)
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "Professor added to offering successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

# -----------------------------------------------------------
# Fetch a single video for Watch Video Page
# -----------------------------------------------------------
def get_video_by_id(video_id: str):
    """
    Fetch a single video's metadata by video_id.
    Includes joins for course_name and course_id.
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

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
            LEFT JOIN CourseOfferings co ON v.offering_id = co.offering_id
            LEFT JOIN Courses c ON co.course_id = c.course_id
            WHERE v.video_id = %s
        """

        cursor.execute(query, (video_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Video not found")

        # HATEOAS item link
        row["links"] = [
            {"rel": "self", "href": f"/videos/{video_id}"},
            {"rel": "course", "href": f"/courses/{row['course_id']}"} if row["course_id"] else {}
        ]

        return row

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


# -----------------------------------------------------------
# Get professor by offeringID
# -----------------------------------------------------------

def get_offerings():
    """
    Retrieves all offerings

        
    Returns:
        A list of dictionaries, where each dictionary represents a row 
        (e.g., {'prof_uni': 'ts3747'}).
    """
    
    # 1. SQL Query using %s placeholder (required for mysql-connector)
    query = """
        SELECT * FROM CourseOfferings
    """
    
    
    try:
        # Use the context manager to automatically close the connection
        with get_db_connection() as conn:
            # Use dictionary=True to get results as dicts instead of tuples
            cursor = conn.cursor(dictionary=True) 

            cursor.execute(query)
            
            # Fetch all rows that match the query
            rows = cursor.fetchall()

            # The connection and cursor are closed automatically by the 'with' block

            return rows

    except Exception as e:
        # Re-raise the error as an HTTPException for the API layer to handle
        raise HTTPException(status_code=500, detail=f"DB error retrieving instructors: {str(e)}")
