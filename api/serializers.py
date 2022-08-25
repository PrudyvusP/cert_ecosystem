from pydantic import BaseModel, validator
from organizations.models import Region


class RegionExistsError(Exception):
    pass


class RegionPostModel(BaseModel):
    region_id: int
    name: str

    @validator("region_id")
    @classmethod
    def region_id_is_valid(cls, value):
        if value > 500:
            raise RegionExistsError
        if Region.query.get(value).exists():
            raise RegionExistsError()
        return value
