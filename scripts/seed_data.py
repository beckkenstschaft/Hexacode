#!/usr/bin/env python3
"""Seed database with sample data."""

import asyncio
import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session_factory
from app.db.models import Session, TranscriptSegment, Summary


async def seed_data() -> None:
    """Seed database with sample sessions."""
    session_factory = get_session_factory()

    async with session_factory() as session:
        # Create sample sessions
        sessions = [
            Session(
                id=uuid.uuid4(),
                title="Team Standup Meeting",
                language="en",
                started_at=datetime.now() - timedelta(days=1),
                ended_at=datetime.now() - timedelta(days=1, hours=-1),
                status="completed",
            ),
            Session(
                id=uuid.uuid4(),
                title="हिंदी कक्षा सत्र",
                language="hi",
                started_at=datetime.now() - timedelta(hours=2),
                ended_at=datetime.now() - timedelta(hours=1),
                status="completed",
            ),
            Session(
                id=uuid.uuid4(),
                title="Hinglish Project Discussion",
                language="hi",
                started_at=datetime.now() - timedelta(minutes=30),
                status="active",
            ),
        ]

        for s in sessions:
            session.add(s)

        await session.flush()

        # Add transcript segments for completed sessions
        segments_data = [
            # Session 1
            (sessions[0].id, 0, 5000, "Good morning everyone, let's start our standup.", "en", "CPU", False),
            (sessions[0].id, 5000, 12000, "Yesterday I completed the API integration.", "en", "CPU", False),
            (sessions[0].id, 12000, 18000, "Today I'll work on the frontend components.", "en", "CPU", False),
            (sessions[0].id, 18000, 22000, "No blockers at the moment.", "en", "CPU", False),
            # Session 2
            (sessions[1].id, 0, 6000, "नमस्ते छात्रों, आज हम नया विषय शुरू करेंगे।", "hi", "CPU", False),
            (sessions[1].id, 6000, 14000, "पहले हम पिछले पाठ की समीक्षा करेंगे।", "hi", "CPU", False),
            (sessions[1].id, 14000, 20000, "फिर हम नए शब्द सीखेंगे।", "hi", "CPU", False),
        ]

        for session_id, start_ms, end_ms, text, lang, provider, simulated in segments_data:
            segment = TranscriptSegment(
                id=uuid.uuid4(),
                session_id=session_id,
                start_ms=start_ms,
                end_ms=end_ms,
                text=text,
                language=lang,
                provider=provider,
                simulated=simulated,
            )
            session.add(segment)

        # Add summaries for completed sessions
        summaries_data = [
            (sessions[0].id, ["API integration completed", "Frontend work planned"], ["Review PR #42", "Update docs"], "CPU", False),
            (sessions[1].id, ["पिछले पाठ की समीक्षा", "नए शब्द सिखाए"], ["अभ्यास कार्य दें", "अगली कक्षा की तैयारी"], "CPU", False),
        ]

        for session_id, key_points, action_items, provider, simulated in summaries_data:
            summary = Summary(
                id=uuid.uuid4(),
                session_id=session_id,
                key_points=key_points,
                action_items=action_items,
                provider=provider,
                simulated=simulated,
                created_at=datetime.now(),
            )
            session.add(summary)

        await session.commit()
        print(f"Seeded {len(sessions)} sessions with transcripts and summaries")


def main() -> int:
    asyncio.run(seed_data())
    return 0


if __name__ == "__main__":
    main()