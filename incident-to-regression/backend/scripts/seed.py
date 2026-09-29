#!/usr/bin/env python
import asyncio
import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session_factory, get_engine
from app.db.models.exam import Student, Exam, Question, AnswerOption
from app.core.config import get_settings

async def seed_db():
    print("Seeding database...")
    engine = get_engine(get_settings())
    SessionFactory = get_session_factory(engine)
    
    async with SessionFactory() as session:
        # Create Students
        student1 = Student(name="Alice Engineer", email="alice@example.com")
        student2 = Student(name="Bob Tester", email="bob@example.com")
        session.add_all([student1, student2])
        
        # Create Exam
        exam = Exam(
            title="Distributed Systems Reliability Assessment",
            description="Testing knowledge of eventual consistency, CAP theorem, and event sourcing.",
            duration_seconds=3600,
            status="PUBLISHED"
        )
        session.add(exam)
        await session.flush()
        
        # Create Questions
        q1 = Question(
            exam_id=exam.id, question_number=1,
            question_text="Which of the following guarantees that a transaction is all-or-nothing?",
            question_type="MULTIPLE_CHOICE"
        )
        session.add(q1)
        await session.flush()
        
        session.add_all([
            AnswerOption(question_id=q1.id, option_key="A", option_text="Atomicity"),
            AnswerOption(question_id=q1.id, option_key="B", option_text="Consistency"),
            AnswerOption(question_id=q1.id, option_key="C", option_text="Isolation"),
            AnswerOption(question_id=q1.id, option_key="D", option_text="Durability")
        ])
        
        q2 = Question(
            exam_id=exam.id, question_number=2,
            question_text="What pattern prevents duplicate event processing?",
            question_type="MULTIPLE_CHOICE"
        )
        session.add(q2)
        await session.flush()
        
        session.add_all([
            AnswerOption(question_id=q2.id, option_key="A", option_text="Two-Phase Commit"),
            AnswerOption(question_id=q2.id, option_key="B", option_text="Idempotency Key"),
            AnswerOption(question_id=q2.id, option_key="C", option_text="Circuit Breaker")
        ])
        
        try:
            await session.commit()
            print("Successfully seeded Phase 2 data!")
        except Exception as e:
            await session.rollback()
            print(f"Error seeding data (might already exist): {e}")

if __name__ == "__main__":
    asyncio.run(seed_db())
