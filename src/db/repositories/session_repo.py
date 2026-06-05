from datetime import datetime, timezone
from typing import List, Optional

from src.db.client import mongo_client
from src.db.models import SessionMetadata


class SessionRepository:
    def __init__(self):
        self.collection = mongo_client.get_collection("sessions")

    async def create_session(self, session: SessionMetadata):
        document = session.model_dump()
        await self.collection.insert_one(document)
        return document

    async def update_session_result(
        self,
        session_id: str,
        status: str,
        agent_logs: List[str],
        errors: List[str],
        final_report: Optional[str],
        chart_titles: List[str],
    ):
        await self.collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "status": status,
                    "agent_logs": agent_logs,
                    "errors": errors,
                    "final_report": final_report,
                    "chart_titles": chart_titles,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

    async def get_session_by_id(self, session_id: str):
        return await self.collection.find_one({"session_id": session_id})