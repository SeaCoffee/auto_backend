from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProfileDataClass:
    id:int
    name:str
    surname:str
    age:int
    city:str
    avatar:str
    created_at:datetime
    updated_at:datetime


@dataclass
class UserDataClass:
    id:int
    username:str
    email:str
    password:str
    is_active:bool
    is_superuser:bool
    is_staff:bool
    role:str
    account_type:str
    created_at: datetime
    updated_at: datetime
    profile:ProfileDataClass

@dataclass
class ListingDataClass:
    id: int
    seller_id: int
    car_id: int
    title: str
    description: str
    listing_photo: str
    active: bool
    created_at: datetime
    updated_at: datetime