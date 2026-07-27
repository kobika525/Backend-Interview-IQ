import os
os.environ['DATABASE_URL']='sqlite:///./test_interview_iq.db'
from fastapi.testclient import TestClient
from app.database import Base,engine
from app.main import app
import app.models
import pytest
@pytest.fixture(autouse=True)
def db_reset():
 Base.metadata.drop_all(engine); Base.metadata.create_all(engine); yield; Base.metadata.drop_all(engine)
@pytest.fixture
def client(): return TestClient(app)
