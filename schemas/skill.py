from pydantic import BaseModel, Field
class UpsertUserSkillRequest(BaseModel):
    proficiency: int = Field(ge=1, le=5)
