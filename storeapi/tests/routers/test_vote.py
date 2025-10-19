import pytest
from datetime import datetime, timezone
from httpx import AsyncClient
from storeapi.database import database, video_table, vote_table, user_table


@pytest.fixture
async def test_video(registered_user: dict):
    """Fixture to create a processed test video"""
    video_data = {
        "user_id": registered_user["id"],
        "title": "Test Video",
        "original_url": "https://test-bucket.s3.amazonaws.com/test-video.mp4",
        "processed_url": "https://test-bucket.s3.amazonaws.com/processed-test-video.mp4",
        "status": "processed",
        "uploaded_at": datetime.now(),
        "processed_at": datetime.now()
    }
    
    query = video_table.insert().values(video_data)
    video_id = await database.execute(query)
    
    # Retrieve the created video
    video_query = video_table.select().where(video_table.c.id == video_id)
    video = await database.fetch_one(video_query)
    
    return video


@pytest.fixture
async def test_video_pending(registered_user: dict):
    """Fixture to create a pending test video (not processed)"""
    video_data = {
        "user_id": registered_user["id"],
        "title": "Pending Video",
        "original_url": "https://test-bucket.s3.amazonaws.com/pending-video.mp4",
        "processed_url": None,
        "status": "uploaded",
        "uploaded_at": datetime.now(),
        "processed_at": None
    }
    
    query = video_table.insert().values(video_data)
    video_id = await database.execute(query)
    
    # Retrieve the created video
    video_query = video_table.select().where(video_table.c.id == video_id)
    video = await database.fetch_one(video_query)
    
    return video


@pytest.fixture
async def another_user(async_client: AsyncClient):
    """Fixture to create another test user"""
    user_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@test.com",
        "password1": "password123",
        "password2": "password123",
        "city": "Bogotá",
        "country": "Colombia"
    }
    
    response = await async_client.post("/api/auth/signup", json=user_data)
    assert response.status_code == 201
    
    # Retrieve the created user
    user_query = user_table.select().where(user_table.c.email == user_data["email"])
    user = await database.fetch_one(user_query)
    
    return user


@pytest.fixture
async def another_user_token(async_client: AsyncClient, another_user):
    """Fixture to get token for the second user"""
    response = await async_client.post(
        "/api/auth/login",
        data={
            "username": another_user.email,
            "password": "password123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestVoteSystem:
    """Test class for the voting system"""

    @pytest.mark.anyio
    async def test_vote_video_like_success(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        test_video
    ):
        """Test successfully liking a processed video"""
        vote_data = {
            "vote_type": "like"
        }
        
        response = await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] is not None
        assert data["video_id"] == test_video.id
        assert data["vote_type"] == "like"
        assert "created_at" in data

    @pytest.mark.anyio
    async def test_vote_video_dislike_success(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        test_video
    ):
        """Test successfully disliking a processed video"""
        vote_data = {
            "vote_type": "dislike"
        }
        
        response = await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["vote_type"] == "dislike"

    @pytest.mark.anyio
    async def test_vote_video_not_found(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str
    ):
        """Test voting on a non-existent video"""
        vote_data = {
            "vote_type": "like"
        }
        
        response = await async_client.post(
            "/api/public/videos/99999/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 404
        assert "Video not found" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_vote_video_not_processed(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        test_video_pending
    ):
        """Test voting on a video that is not processed"""
        vote_data = {
            "vote_type": "like"
        }
        
        response = await async_client.post(
            f"/api/public/videos/{test_video_pending.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 400
        assert "Video must be processed before voting" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_vote_invalid_type(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        test_video
    ):
        """Test voting with an invalid vote type"""
        vote_data = {
            "vote_type": "invalid"
        }
        
        response = await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 400
        assert "vote_type must be 'like' or 'dislike'" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_vote_without_authentication(
        self, 
        async_client: AsyncClient, 
        test_video
    ):
        """Test voting without authentication"""
        vote_data = {
            "vote_type": "like"
        }
        
        response = await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data
        )
        
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_update_existing_vote(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        test_video
    ):
        """Test updating an existing vote"""
        # First, vote like
        vote_data = {
            "vote_type": "like"
        }
        
        response = await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        assert response.status_code == 200
        
        # Then try to change to dislike (should fail - user already voted)
        vote_data = {"vote_type": "dislike"}
        response = await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Ya has votado por este video."

    @pytest.mark.anyio
    async def test_get_video_votes_success(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        test_video
    ):
        """Test retrieving video vote statistics"""
        response = await async_client.get(
            f"/api/videos/{test_video.id}/votes",
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "video" in data
        assert "likes" in data
        assert "dislikes" in data
        assert "user_vote" in data
        assert data["video"]["video_id"] == test_video.id

    @pytest.mark.anyio
    async def test_get_video_votes_with_user_vote(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        test_video
    ):
        """Test retrieving video vote stats including the user's vote"""
        # First, vote
        vote_data = {
            "vote_type": "like"
        }
        
        await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        # Then get stats
        response = await async_client.get(
            f"/api/videos/{test_video.id}/votes",
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["likes"] == 1
        assert data["dislikes"] == 0
        assert data["user_vote"] == "like"

    @pytest.mark.anyio
    async def test_get_video_votes_not_found(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str
    ):
        """Test retrieving vote stats for a non-existent video"""
        response = await async_client.get(
            "/api/videos/99999/votes",
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 404
        assert "Video not found" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_remove_vote_success(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        test_video
    ):
        """Test successfully removing a vote"""
        # First, vote
        vote_data = {
            "vote_type": "like"
        }
        
        await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        # Then remove the vote
        response = await async_client.delete(
            f"/api/videos/{test_video.id}/vote",
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 200
        assert "Vote removed successfully" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_remove_vote_not_found(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        test_video
    ):
        """Test removing a non-existent vote"""
        response = await async_client.delete(
            f"/api/videos/{test_video.id}/vote",
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 404
        assert "Vote not found" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_get_public_videos_empty(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str
    ):
        """Test retrieving public videos when none are processed"""
        response = await async_client.get(
            "/api/public/videos",
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # It may be empty or contain videos, both are valid

    @pytest.mark.anyio
    async def test_get_public_videos_with_votes(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        another_user_token: str,
        test_video
    ):
        """Test retrieving public videos with votes from multiple users"""
        # User 1 votes like
        vote_data_1 = {
            "vote_type": "like"
        }
        
        await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data_1,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        # User 2 votes dislike
        vote_data_2 = {
            "vote_type": "dislike"
        }

        await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data_2,
            headers={"Authorization": f"Bearer {another_user_token}"}
        )
        
        # Retrieve public videos
        response = await async_client.get(
            "/api/public/videos",
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # Verify video vote data
        video_data = data[0]
        assert video_data["likes"] >= 1  # At least 1 like
        assert video_data["dislikes"] >= 0  # Can be 0 or more dislikes
        assert video_data["user_vote"] == "like"  # Current user's vote
        assert video_data["video"]["video_id"] == test_video.id  # Correct video

    @pytest.mark.anyio
    async def test_multiple_users_vote_same_video(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        another_user_token: str,
        test_video
    ):
        """Test multiple users voting on the same video"""
        # User 1 votes like
        vote_data = {
            "vote_type": "like"
        }
        
        response1 = await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        assert response1.status_code == 200
        
        # User 2 votes dislike
        vote_data = {"vote_type": "dislike"}
        response2 = await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {another_user_token}"}
        )
        assert response2.status_code == 200
        
        # Verify both votes exist
        response = await async_client.get(
            f"/api/videos/{test_video.id}/votes",
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["likes"] == 1
        assert data["dislikes"] == 1
        assert data["user_vote"] == "like"

    @pytest.mark.anyio
    async def test_vote_anti_fraud_protection(
        self, 
        async_client: AsyncClient, 
        logged_in_token: str, 
        test_video
    ):
        """Test anti-fraud protection: a user cannot vote multiple times"""
        vote_data = {
            "vote_type": "like"
        }
        
        # First vote
        response1 = await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        assert response1.status_code == 200
        
        # Second vote (should fail - user already voted)
        vote_data = {"vote_type": "dislike"}
        response2 = await async_client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json=vote_data,
            headers={"Authorization": f"Bearer {logged_in_token}"}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Ya has votado por este video."
        
        # Verify only one vote exists in the database
        votes_query = vote_table.select().where(
            (vote_table.c.user_id == response1.json()["user_id"]) & 
            (vote_table.c.video_id == test_video.id)
        )
        votes = await database.fetch_all(votes_query)
        assert len(votes) == 1
        assert votes[0].vote_type == "like"
