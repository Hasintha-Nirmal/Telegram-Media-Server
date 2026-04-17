from sqlalchemy import select, or_, and_
from database.models import Media, Chat
from datetime import datetime


class SearchEngine:
    def __init__(self, db_session):
        self.db = db_session
    
    async def search_media(
        self,
        query=None,
        media_type=None,
        chat_id=None,
        min_size=None,
        max_size=None,
        start_date=None,
        end_date=None,
        limit=100,
        offset=0
    ):
        """Search media with filters"""
        stmt = select(Media).join(Chat)
        
        filters = []
        
        # Text search
        if query:
            filters.append(
                or_(
                    Media.file_name.ilike(f'%{query}%'),
                    Chat.name.ilike(f'%{query}%')
                )
            )
        
        # Media type filter
        if media_type:
            filters.append(Media.media_type == media_type)
        
        # Chat filter
        if chat_id:
            filters.append(Media.chat_id == chat_id)
        
        # Size filters
        if min_size:
            filters.append(Media.file_size >= min_size)
        if max_size:
            filters.append(Media.file_size <= max_size)
        
        # Date filters
        if start_date:
            filters.append(Media.upload_date >= start_date)
        if end_date:
            filters.append(Media.upload_date <= end_date)
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        # Apply pagination
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_stats(self):
        """Get media statistics"""
        from sqlalchemy import func
        
        # Total chats
        result = await self.db.execute(select(func.count(Chat.id)))
        total_chats = result.scalar()
        
        # Total media
        result = await self.db.execute(select(func.count(Media.id)))
        total_media = result.scalar()
        
        # Total storage
        result = await self.db.execute(select(func.sum(Media.file_size)))
        total_storage = result.scalar() or 0
        
        # Media by type
        result = await self.db.execute(
            select(Media.media_type, func.count(Media.id))
            .group_by(Media.media_type)
        )
        media_by_type = {row[0]: row[1] for row in result}
        
        return {
            'total_chats': total_chats,
            'total_media': total_media,
            'total_storage': total_storage,
            'media_by_type': media_by_type
        }
