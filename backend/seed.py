"""초기 데이터 시드 스크립트: 기본 슈퍼 관리자 계정 생성."""

import asyncio

from sqlalchemy import select
from app.database import async_session_maker, init_db
from app.models.admin import Admin
from app.utils.security import hash_password


async def seed():
    await init_db()

    async with async_session_maker() as session:
        # 기존 슈퍼 관리자 확인
        result = await session.execute(
            select(Admin).where(Admin.role == "SUPER_ADMIN")
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"슈퍼 관리자가 이미 존재합니다: {existing.username}")
            return

        # 기본 슈퍼 관리자 생성
        admin = Admin(
            store_id=None,
            username="admin",
            password_hash=hash_password("admin1234"),
            role="SUPER_ADMIN",
        )
        session.add(admin)
        await session.commit()
        print("기본 슈퍼 관리자 생성 완료: admin / admin1234")
        print("⚠️  첫 로그인 후 비밀번호를 변경해주세요.")


if __name__ == "__main__":
    asyncio.run(seed())
