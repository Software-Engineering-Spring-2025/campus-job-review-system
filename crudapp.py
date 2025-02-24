from app import app, db
from app.models import Vacancies
import logging


def insertVacancyData():
    Vacancies.query.delete()
    createVacancies(
        "Cashier",
        "Cashier Job Description",
        "Talley Student Union",
        "9.25$ per hour",
        15,
    )
    createVacancies(
        "Application Developer",
        "Developer Job Description",
        "Venture IV",
        "25$ per hour",
        20,
    )
    createVacancies(
        "Gym Trainer",
        "Trainer Job Description",
        "Talley Student Union",
        "12.5$ per hour",
        20,
    )
    createVacancies(
        "Course Instructor",
        "Course Instructor Description",
        "Talley Student Union",
        "9.5$ per hour",
        18,
    )
    createVacancies(
        "Course Grader",
        "Course Grader Job Description",
        "Talley Student Union",
        "10.95$ per hour",
        20,
    )
    createVacancies(
        "Cleaner",
        "Fountain Dining",
        "Bragaww Hall",
        "11.55$ per hour",
        12)
    createVacancies(
        "Sports Instructor",
        "Sports Instructor Description",
        "Talley Student Union",
        "12.75$ per hour",
        16,
    )


def createVacancies(
    jobTitle, jobDescription, jobLocation, payRate, maxHoursAllowed
):  # create new user
    newVacancy = Vacancies(
        jobTitle, jobDescription, jobLocation, payRate, maxHoursAllowed
    )
    db.session.add(newVacancy)
    db.session.commit()


if __name__ == "__main__":
    insertVacancyData()
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.run(debug=True)
