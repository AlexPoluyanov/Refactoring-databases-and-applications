CREATE INDEX idx_cars_car_num ON cars (car_num);
CREATE INDEX idx_cars_year_of_issue ON cars (year_of_issue);
CREATE INDEX idx_cars_color_body_type ON cars (color, car_body_type);

CREATE INDEX idx_photos_car_num ON photos (car_num);
CREATE INDEX idx_photos_date ON photos (date);

CREATE INDEX idx_insurance_car_num ON insurance (car_num);
CREATE INDEX idx_insurance_date_range ON insurance (start_date, end_date);
CREATE INDEX idx_insurance_company ON insurance (company);

CREATE INDEX idx_crashes_car_num ON crashes (car_num);
CREATE INDEX idx_crashes_date ON crashes (date);
