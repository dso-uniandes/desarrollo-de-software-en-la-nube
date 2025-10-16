import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import func, select
from storeapi.database import database, vote_table, video_table
from storeapi.models.video import VideoOut
from storeapi.models.vote import VoteIn, Vote, VideoWithVotes
from storeapi.models.user import UserOut
from storeapi.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/videos/vote", response_model=Vote, status_code=201)
async def vote_video(
    vote: VoteIn, 
    current_user: Annotated[UserOut, Depends(get_current_user)]
):
    """
    Vote for a video (like or dislike).
    If the user has already voted, update their vote.
    """
    logger.info(f"User {current_user.id} voting {vote.vote_type} on video {vote.video_id}")
    
    # Validate that the vote type is valid
    if vote.vote_type not in ["like", "dislike"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="vote_type must be 'like' or 'dislike'"
        )
    
    # Check that the video exists
    video_query = video_table.select().where(video_table.c.id == vote.video_id)
    video = await database.fetch_one(video_query)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check that the video is processed (only processed videos can be voted on)
    if video.status != "processed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video must be processed before voting"
        )
    
    # Check if the user has already voted for this video
    existing_vote_query = vote_table.select().where(
        (vote_table.c.user_id == current_user.id) & 
        (vote_table.c.video_id == vote.video_id)
    )
    existing_vote = await database.fetch_one(existing_vote_query)
    
    if existing_vote:
        # Update existing vote
        update_query = vote_table.update().where(
            vote_table.c.id == existing_vote.id
        ).values(vote_type=vote.vote_type)
        
        await database.execute(update_query)
        logger.info(f"Updated vote for user {current_user.id} on video {vote.video_id}")
        
        return {
            "id": existing_vote.id,
            "user_id": current_user.id,
            "video_id": vote.video_id,
            "vote_type": vote.vote_type,
            "created_at": existing_vote.created_at
        }
    else:
        # Create a new vote
        insert_query = vote_table.insert().values(
            user_id=current_user.id,
            video_id=vote.video_id,
            vote_type=vote.vote_type
        )
        
        last_record_id = await database.execute(insert_query)
        logger.info(f"Created new vote for user {current_user.id} on video {vote.video_id}")
        
        # Retrieve the created vote to return the actual created_at
        new_vote_query = vote_table.select().where(vote_table.c.id == last_record_id)
        new_vote = await database.fetch_one(new_vote_query)
        
        return {
            "id": last_record_id,
            "user_id": current_user.id,
            "video_id": vote.video_id,
            "vote_type": vote.vote_type,
            "created_at": new_vote.created_at
        }


@router.delete("/api/videos/{video_id}/vote", status_code=200)
async def remove_vote(
    video_id: int,
    current_user: Annotated[UserOut, Depends(get_current_user)]
):
    """
    Remove the user's vote from a specific video.
    """
    logger.info(f"User {current_user.id} removing vote from video {video_id}")
    
    # Find the user's vote for this video
    vote_query = vote_table.select().where(
        (vote_table.c.user_id == current_user.id) & 
        (vote_table.c.video_id == video_id)
    )
    vote = await database.fetch_one(vote_query)
    
    if not vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote not found"
        )
    
    # Delete the vote
    delete_query = vote_table.delete().where(vote_table.c.id == vote.id)
    await database.execute(delete_query)
    
    logger.info(f"Removed vote for user {current_user.id} from video {video_id}")
    return {"detail": "Vote removed successfully"}


@router.get("/api/videos/{video_id}/votes", response_model=VideoWithVotes)
async def get_video_votes(
    video_id: int,
    current_user: Annotated[UserOut, Depends(get_current_user)]
):
    """
    Retrieve vote statistics for a specific video.
    """
    logger.info(f"Getting votes for video {video_id}")
    
    # Get the video
    video_query = video_table.select().where(video_table.c.id == video_id)
    video = await database.fetch_one(video_query)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Count likes and dislikes
    likes_query = vote_table.select().where(
        (vote_table.c.video_id == video_id) & 
        (vote_table.c.vote_type == "like")
    )
    likes = await database.fetch_all(likes_query)
    
    dislikes_query = vote_table.select().where(
        (vote_table.c.video_id == video_id) & 
        (vote_table.c.vote_type == "dislike")
    )
    dislikes = await database.fetch_all(dislikes_query)
    
    # Get the current user's vote
    user_vote_query = vote_table.select().where(
        (vote_table.c.user_id == current_user.id) & 
        (vote_table.c.video_id == video_id)
    )
    user_vote = await database.fetch_one(user_vote_query)
    
    # Convert video to VideoOut
    video_out = VideoOut(
        video_id=video.id,
        title=video.title,
        status=video.status,
        uploaded_at=video.uploaded_at,
        processed_at=video.processed_at,
        processed_url=video.processed_url
    )
    
    return VideoWithVotes(
        video=video_out,
        likes=len(likes),
        dislikes=len(dislikes),
        user_vote=user_vote.vote_type if user_vote else None
    )


@router.get("/api/videos/public/all", response_model=list[VideoWithVotes])
async def get_public_videos(
    current_user: Annotated[UserOut, Depends(get_current_user)]
):
    """
    Retrieve all processed videos with vote statistics.
    Public endpoint so users can view and vote on videos.
    """
    logger.info("Getting public videos")
    
    # Get all processed videos
    videos_query = video_table.select().where(video_table.c.status == "processed")
    videos = await database.fetch_all(videos_query)
    
    public_videos = []
    
    for video in videos:
        # Count likes and dislikes for each video
        likes_query = vote_table.select().where(
            (vote_table.c.video_id == video.id) & 
            (vote_table.c.vote_type == "like")
        )
        likes = await database.fetch_all(likes_query)
        
        dislikes_query = vote_table.select().where(
            (vote_table.c.video_id == video.id) & 
            (vote_table.c.vote_type == "dislike")
        )
        dislikes = await database.fetch_all(dislikes_query)
        
        # Get the current user's vote
        user_vote_query = vote_table.select().where(
            (vote_table.c.user_id == current_user.id) & 
            (vote_table.c.video_id == video.id)
        )
        user_vote = await database.fetch_one(user_vote_query)
        
        # Convert to VideoOut
        video_out = VideoOut(
            video_id=video.id,
            title=video.title,
            status=video.status,
            uploaded_at=video.uploaded_at,
            processed_at=video.processed_at,
            processed_url=video.processed_url
        )
        
        public_videos.append(VideoWithVotes(
            video=video_out,
            likes=len(likes),
            dislikes=len(dislikes),
            user_vote=user_vote.vote_type if user_vote else None
        ))
    
    return public_videos
