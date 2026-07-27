from pydantic import BaseModel, Field
class CreateTicketRequest(BaseModel):
    subject: str = Field(min_length=3, max_length=180)
    category: str = Field(min_length=2, max_length=50)
    message: str = Field(min_length=1)
class AddMessageRequest(BaseModel):
    message: str = Field(min_length=1)
