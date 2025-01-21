from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, SmallInteger, Enum, Numeric, Text, Date, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import enum

DATABASE_URL = "postgresql://postgres:postgres@localhost/refractor"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums for custom types
class NumType(str, enum.Enum):
    individual = "individual"
    legal_entity = "legal_entity"
    forigner_citizen = "forigner_citizen"
    army = "army"

class CarBodyType(str, enum.Enum):
    sedan = "sedan"
    limousine = "limousine"
    hatchback = "hatchback"
    liftback = "liftback"
    universal = "universal"
    coupe = "coupe"
    convertible = "convertible"
    cabriolet = "cabriolet"
    roadster = "roadster"
    targa = "targa"
    minivan = "minivan"
    pickup = "pickup"
    truck = "truck"
    crossover = "crossover"
    other = "other"

class TransmissionType(str, enum.Enum):
    variator = "variator"
    mechanical = "mechanical"
    automatic = "automatic"
    robotic = "robotic"

class WheelDriveType(str, enum.Enum):
    front_wheel = "front_wheel"
    rear_wheel = "rear_wheel"
    all_wheel = "all_wheel"

class Rudder(str, enum.Enum):
    left = "left"
    right = "right"

# Database models
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    surname = Column(String(128), nullable=False)
    username = Column(String(256), unique=True, nullable=False)
    phone = Column(String(16), nullable=False)
    hash = Column(String(256), nullable=False)
    salt = Column(String(256), nullable=False)

class CarDB(Base):
    __tablename__ = "cars"

    car_num = Column(String(16), primary_key=True, index=True)
    num_type = Column(Enum(NumType), nullable=False)
    year_of_issue = Column(SmallInteger, nullable=False)
    color = Column(String(32), nullable=True)
    car_body_type = Column(Enum(CarBodyType), nullable=False)
    transmission = Column(Enum(TransmissionType), nullable=False)
    wheel_drive_type = Column(Enum(WheelDriveType), nullable=False)
    rudder = Column(Enum(Rudder), nullable=False)

    __table_args__ = (
        CheckConstraint("year_of_issue > 1884", name="check_year_of_issue"),
    )

class PhotoDB(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    car_num = Column(String(16), ForeignKey("cars.car_num"), nullable=False)
    link = Column(String(256), nullable=False)
    date = Column(Date, nullable=False)
    added_by = Column(Integer, ForeignKey("users.id"), nullable=False)

class InsuranceDB(Base):
    __tablename__ = "insurance"

    id = Column(Integer, primary_key=True, index=True)
    car_num = Column(String(16), ForeignKey("cars.car_num"), nullable=False)
    company = Column(String(256), nullable=False)
    type = Column(String(128), nullable=False)
    amount = Column(Numeric(15, 2), nullable=True)
    price = Column(Numeric(15, 2), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

class CrashDB(Base):
    __tablename__ = "crashes"

    id = Column(Integer, primary_key=True, index=True)
    car_num = Column(String(16), ForeignKey("cars.car_num"), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)

# Pydantic models
class User(BaseModel):
    id: int
    name: str
    surname: str
    username: str
    phone: str

    class Config:
        orm_mode = True

class Car(BaseModel):
    car_num: str
    num_type: NumType
    year_of_issue: int
    color: Optional[str] = None
    car_body_type: CarBodyType
    transmission: TransmissionType
    wheel_drive_type: WheelDriveType
    rudder: Rudder

    class Config:
        orm_mode = True

class Photo(BaseModel):
    id: int
    car_num: str
    link: str
    date: str
    added_by: int

    class Config:
        orm_mode = True

class Insurance(BaseModel):
    id: int
    car_num: str
    company: str
    type: str
    amount: Optional[float] = None
    price: Optional[float] = None
    start_date: str
    end_date: str

    class Config:
        orm_mode = True

class Crash(BaseModel):
    id: int
    car_num: str
    date: str
    description: Optional[str] = None

    class Config:
        orm_mode = True

cars = []
photos = []
insurances = []
crashes = []

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/cars", response_model=List[Car])
def get_cars(db: Session = Depends(get_db)):
    """Retrieve the list of all cars."""
    return db.query(CarDB).all()

@app.get("/cars/{car_num}", response_model=Car)
def get_car(car_num: str, db: Session = Depends(get_db)):
    """Retrieve a car by its number."""
    car = db.query(CarDB).filter(CarDB.car_num == car_num).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@app.post("/cars", response_model=Car, status_code=201)
def create_car(car: Car, db: Session = Depends(get_db)):
    """Add a new car to the database."""
    existing_car = db.query(CarDB).filter(CarDB.car_num == car.car_num).first()
    if existing_car:
        raise HTTPException(status_code=400, detail="Car with this number already exists")
    new_car = CarDB(**car.dict())
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

@app.put("/cars/{car_num}", response_model=Car)
def update_car(car_num: str, updated_car: Car, db: Session = Depends(get_db)):
    """Update details of an existing car."""
    car = db.query(CarDB).filter(CarDB.car_num == car_num).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    for key, value in updated_car.dict().items():
        setattr(car, key, value)
    db.commit()
    db.refresh(car)
    return car

@app.delete("/cars/{car_num}", response_model=Car)
def delete_car(car_num: str, db: Session = Depends(get_db)):
    """Delete a car from the database by its number."""
    car = db.query(CarDB).filter(CarDB.car_num == car_num).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Delete related records from dependent tables
    db.query(PhotoDB).filter(PhotoDB.car_num == car_num).delete()
    db.query(InsuranceDB).filter(InsuranceDB.car_num == car_num).delete()
    db.query(CrashDB).filter(CrashDB.car_num == car_num).delete()
    
    # Delete the car
    db.delete(car)
    db.commit()
    return car

@app.get("/photos", response_model=List[Photo], summary="Получить список фотографий")
def get_photos():
    return photos

@app.post("/photos", response_model=Photo, status_code=201, summary="Добавить фотографию")
def add_photo(photo: Photo):
    photos.append(photo)
    return photo

@app.get("/insurance", response_model=List[Insurance], summary="Получить список страховок")
def get_insurances():
    return insurances

@app.post("/insurance", response_model=Insurance, status_code=201, summary="Добавить страховку")
def add_insurance(insurance: Insurance):
    insurances.append(insurance)
    return insurance

@app.get("/crashes", response_model=List[Crash], summary="Получить список аварий")
def get_crashes():
    return crashes

@app.post("/crashes", response_model=Crash, status_code=201, summary="Добавить информацию об аварии")
def add_crash(crash: Crash):
    crashes.append(crash)
    return crash



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
