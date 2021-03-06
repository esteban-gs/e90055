from pydantic.types import Json
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.sqltypes import JSON
from starlette import status
from api.dependencies.db import get_db
from api.core.security import get_password_hash
from api.models import User, Prospect, Campaign, CampaignProspect, ProspectsFile
from api.models.prospect_files import ImportStatus


def seed_data(db: Session):
    print("-- Seeding Data --")
    # Create user
    user1 = User(email="test@test.com", password_digest=get_password_hash("sample"))
    db.add(user1)

    prospectFiles1 = ProspectsFile(
        file_address="server/files/file1.csv",
        status=ImportStatus.complete,
        user=user1,
    )
    db.add(prospectFiles1)

    for i in range(20):
        # Create campaigns for user
        campaign = Campaign(name=f"Campaign {i}", user=user1)
        db.add(campaign)
        for j in range(0, 10):
            # Create prospects for user
            prospect = Prospect(
                email=f"prospect{i}{j}@mail.com",
                user=user1,
                first_name=f"John {i}{j}",
                last_name="D.",
            )
            db.add(prospect)
            # Link the prospects to a campaign
            link = CampaignProspect(prospect=prospect, campaign=campaign)
            db.add(link)

    try:
        db.commit()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    db = next(get_db())
    seed_data(db)
