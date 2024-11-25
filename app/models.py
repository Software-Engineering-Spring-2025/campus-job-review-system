from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Reviews(db.Model):
    """Model which stores the information of the reviews submitted"""

    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(64), index=True, nullable=False)
    locations = db.Column(db.String(120), index=True, nullable=False)
    job_title = db.Column(db.String(64), index=True, nullable=False)
    job_description = db.Column(db.String(120), index=True, nullable=False)
    hourly_pay = db.Column(db.String(10), nullable=False)
    benefits = db.Column(db.String(120), index=True, nullable=False)
    review = db.Column(db.String(120), index=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    recommendation = db.Column(db.Integer, nullable=False)
    upvotes = db.Column(db.Integer, default=0)  
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Vacancies(db.Model):
    """Model which stores the information of the reviews submitted"""

    vacancyId = db.Column(db.Integer, primary_key=True)
    jobTitle = db.Column(db.String(500), index=True, nullable=False)
    jobDescription = db.Column(db.String(1000), index=True, nullable=False)
    jobLocation = db.Column(db.String(500), index=True, nullable=False)
    jobPayRate = db.Column(db.String(120), index=True, nullable=False)
    maxHoursAllowed = db.Column(db.Integer, nullable=False)

    def __init__(
        self, jobTitle, jobDescription, jobLocation, jobPayRate, maxHoursAllowed
    ):
        self.jobTitle = jobTitle
        self.jobDescription = jobDescription
        self.jobLocation = jobLocation
        self.jobPayRate = jobPayRate
        self.maxHoursAllowed = maxHoursAllowed


class  User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    reviews = db.relationship("Reviews", backref="author", lazy=True)
    is_recruiter = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class JobApplication(db.Model):
    """Model to store information about job applications"""

    id = db.Column(db.Integer, primary_key=True)
    job_link = db.Column(db.String(255), nullable=False)  
    applied_on = db.Column(db.Date, nullable=False)       
    last_update_on = db.Column(db.Date, nullable=False)   
    status = db.Column(db.String(50), nullable=False)     
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  

    def __repr__(self):
        return f"<JobApplication {self.id} | Status: {self.status}>"
    
    
class Recruiter_Postings(db.Model):
    """Model which stores the information of the postings added by recruiter"""

    __tablename__ = "recruiter_postings"  # Explicit table name

    postingId = db.Column(db.Integer, primary_key=True)
    recruiterId = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    jobTitle = db.Column(db.String(500), index=True, nullable=False)
    jobDescription = db.Column(db.String(1000), index=True, nullable=False)
    jobLink = db.Column(db.String(1000), index=True, nullable=False)
    jobLocation = db.Column(db.String(500), index=True, nullable=False)
    jobPayRate = db.Column(db.String(120), index=True, nullable=False)
    maxHoursAllowed = db.Column(db.Integer, nullable=False)


class PostingApplications(db.Model):
    """Model which stores the information of all applications for each recruiter posting."""

    __tablename__ = "posting_applications"

    postingId = db.Column(db.Integer, db.ForeignKey("recruiter_postings.postingId"), primary_key=True)
    recruiterId = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    applicantId = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    shortlisted = db.Column(db.Boolean, default=False)  # Add shortlisted column

    # Relationships
    recruiter = db.relationship("User", foreign_keys=[recruiterId], backref="applications_reviewed")
    applicant = db.relationship("User", foreign_keys=[applicantId], backref="applications_applied")
    job_posting = db.relationship("Recruiter_Postings", foreign_keys=[postingId], backref="applications")


class JobExperience(db.Model):
    """Model to store job experiences for users."""
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)

class Meetings(db.Model):
    """Model to store meeting information."""
    __tablename__ = "meetings"  # Explicit table name

    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    meeting_time = db.Column(db.DateTime, nullable=False)  # Time of the meeting
    posting_id = db.Column(db.Integer, db.ForeignKey("recruiter_postings.postingId"), nullable=True)  # Optional job posting

    # Relationships
    recruiter = db.relationship("User", foreign_keys=[recruiter_id], backref="recruiter_meetings")
    applicant = db.relationship("User", foreign_keys=[applicant_id], backref="applicant_meetings")
    job_posting = db.relationship("Recruiter_Postings", foreign_keys=[posting_id], backref="meetings")

    def __repr__(self):
        return f"<Meeting {self.id} | Time: {self.meeting_time}>"


