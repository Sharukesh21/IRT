import uuid
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.regression_test import RegressionTest, RegressionSuiteRun
from app.domain.test_runner import RegressionTestRunner

class RegressionSuite:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_suite(self) -> RegressionSuiteRun:
        # Load all ready/active tests
        res = await self.db.execute(select(RegressionTest).where(RegressionTest.status.in_(["READY", "ACTIVE"])))
        tests = res.scalars().all()
        
        suite = RegressionSuiteRun(
            suite_run_id=f"SUITE-{uuid.uuid4().hex[:6].upper()}",
            total_tests=len(tests)
        )
        self.db.add(suite)
        await self.db.commit() # commit early to get ID
        
        runner = RegressionTestRunner(self.db)
        passed = 0
        failed = 0
        errors = 0
        
        for t in tests:
            try:
                run = await runner.run_test(t.id)
                if run.status == "PASSED":
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                errors += 1
                
        suite.passed = passed
        suite.failed = failed
        suite.errors = errors
        suite.pass_rate = (passed / len(tests)) * 100 if len(tests) > 0 else 0
        suite.completed_at = __import__("sqlalchemy.sql").func.now()
        
        self.db.add(suite)
        await self.db.commit()
        
        return suite
