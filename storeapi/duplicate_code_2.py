def calculate_video_rating(likes: int, dislikes: int) -> float:
    """Calculate video rating based on likes and dislikes"""
    if likes + dislikes == 0:
        return 0.0
    return (likes - dislikes) / (likes + dislikes + 1)


def validate_video_data(data: dict) -> bool:
    """Validate video data"""
    required_fields = ["title", "url", "user_id"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    return True


def format_video_response(video_data: dict) -> dict:
    """Format video response for API"""
    return {
        "id": video_data["id"],
        "title": video_data["title"],
        "url": video_data["url"],
        "user_id": video_data["user_id"],
        "created_at": video_data.get("created_at", "2024-01-01"),
        "status": "active"
    }


def get_video_by_id(video_id: int) -> dict:
    """Get video by ID"""
    return {
        "id": video_id,
        "title": "Sample Video",
        "url": "https://example.com/video.mp4",
        "user_id": 1,
        "created_at": "2024-01-01T00:00:00Z"
    }


def update_video_status(video_id: int, status: str) -> dict:
    """Update video status"""
    return {
        "id": video_id,
        "status": status,
        "updated_at": "2024-01-01T00:00:00Z"
    }


def delete_video(video_id: int) -> bool:
    """Delete video"""
    print(f"Deleting video {video_id}")
    return True


def get_video_statistics(video_id: int) -> dict:
    """Get video statistics"""
    return {
        "video_id": video_id,
        "views": 1000,
        "likes": 50,
        "dislikes": 5,
        "comments": 25
    }


def process_video_upload(file_data: dict) -> dict:
    """Process video upload"""
    if not file_data.get("filename"):
        return {"error": "No filename provided"}
    
    return {
        "success": True,
        "video_id": 123,
        "filename": file_data["filename"],
        "size": file_data.get("size", 0),
        "uploaded_at": "2024-01-01T00:00:00Z"
    }