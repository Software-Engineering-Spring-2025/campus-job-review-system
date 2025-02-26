import pytest
from app import app, db
from app.models import User, Reviews, JobApplication, Recruiter_Postings, Meetings, JobExperience, Recruiter_Postings, PostingApplications
from datetime import datetime
from flask import url_for
from flask_login import login_user
from io import BytesIO
import os
import sys
from unittest.mock import patch
import tempfile

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def test_user():
    user = User(username="testuser", email="test@example.com", password="testpass12345!")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def logged_in_client(client, test_user):
    with client.session_transaction() as session:
        session['_user_id'] = test_user.id
    return client


@pytest.fixture
def sample_resume():
    # Create a temporary file for testing resume upload
    temp_dir = tempfile.mkdtemp()  # Create a temporary directory
    resume_path = os.path.join(temp_dir, 'test_resume.pdf')
    with open(resume_path, 'wb') as f:
        f.write(b'This is a sample resume content.')  # Sample content for the file
    return resume_path  # Return the path to the temp file

@pytest.fixture
def test_reviews_for_search(login_user):
    with app.app_context():
        review1 = Reviews(job_title="Software Developer", review="Great job!", author=login_user)
        review2 = Reviews(job_title="Senior Developer", review="Good company", author=login_user)
        review3 = Reviews(job_title="Web Designer", review="Creative work", author=login_user)
        db.session.add_all([review1, review2, review3])
        db.session.commit()

@pytest.fixture
def test_recruiter_posting():
    # Create and add a recruiter posting to the database
    recruiter_posting = Recruiter_Postings(
        recruiterId=1,  # Use an existing user ID or create a test user if needed
        jobTitle="Test Job Title",
        jobDescription="This is a test job description",
        jobLink="http://example.com/job",
        jobLocation="Test Location",
        jobPayRate="$50/hour",
        maxHoursAllowed=40
    )
    db.session.add(recruiter_posting)
    db.session.commit()
    return recruiter_posting

@pytest.fixture
def test_job_experience(test_user):
    job_exp = JobExperience(
        job_title="Software Engineer",
        company_name="Test Company",
        location="Test Location",
        duration="2020-2022",
        description="Test job description",
        skills="Python,Flask",
        username=test_user.username
    )
    db.session.add(job_exp)
    db.session.commit()
    return job_exp
##############################################
## Passing test cases 
##############################################
#1.
def test_serve_resume_not_found(logged_in_client):
    # Test case: Serving a non-existent resume file
    response = logged_in_client.get('/resume/non_existent_resume.pdf')
    assert response.status_code == 404  # File should not be found, expecting a 404

#2.
def test_failed_login(client):
    response = client.post('/login',
                          data={'email': 'invalid@example.com', 'password': 'wrongpass123456'},
                          follow_redirects=True)
    
    # Check that the response is successful (200 OK)
    assert response.status_code == 200
    
    # Check that we're still on the login page or there's an error message
    assert b"Login" in response.data or b"Sign In" in response.data
    assert b"Unsuccessful" in response.data or b"incorrect" in response.data.lower() or b"invalid" in response.data.lower()
#3.
def test_upload_valid_resume(logged_in_client, sample_resume):
    # Open the temporary resume file created by the sample_resume fixture
    with open(sample_resume, 'rb') as f:
        data = {
            'resume': (f, 'test_resume.pdf')  # Use the file object and a filename
        }
        response = logged_in_client.post('/account', data=data, content_type='multipart/form-data', follow_redirects=True)
    
    # Check if the status code is 200 (redirected after successful upload)
    assert response.status_code == 200
    assert b"Resume uploaded successfully!" in response.data  # Check for the flash message
    assert b"test_resume.pdf" in response.data  # Ensure the filename appears in the response

#4.
def test_upload_invalid_resume(logged_in_client, sample_resume):
    # Open the temporary resume file created by the sample_resume fixture
    # Change the file to an invalid type (.exe, for example)
    with open(sample_resume, 'rb') as f:
        data = {
            'resume': (f, 'test_resume.exe')  # Use an invalid file extension (exe)
        }
        response = logged_in_client.post('/account', data=data, content_type='multipart/form-data', follow_redirects=True)
    
    # Check if the status code is 200 (redirected after unsuccessful upload)
    assert response.status_code == 200
    
    # Check for the error flash message indicating an invalid file type
    assert b"Allowed file types are pdf, docx, txt" in response.data  # Check for the error message
    assert b"test_resume.exe" not in response.data  


# 5. Test user logout
def test_logout_user(logged_in_client):
    response = logged_in_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200


#6. Test invalid job posting ID
def test_invalid_job_id(client):
    response = client.get('/job/9999')
    assert response.status_code == 404

#7. Test viewing all reviews
def test_view_all_reviews(client):
    response = client.get('/review/all')
    assert response.status_code == 200

#8. Testi fetch
def test_fetch_profile_get_not_allowed(logged_in_client): # Test that GET is not allowed
    response = logged_in_client.get('/profile')
    assert response.status_code == 405

#9.Test job profile page
def test_job_profile_page(logged_in_client, test_job_experience):
    response = logged_in_client.get('/job_profile')
    assert response.status_code == 200
    assert b"Software Engineer" in response.data
    assert b"Test Company" in response.data

#10. Test tracking 
def test_application_tracker_page(logged_in_client):
    response = logged_in_client.get('/application_tracker')
    assert response.status_code == 200
    assert b"Application Tracker" in response.data

#11. Test adding a job application
def test_add_job_application(logged_in_client):
    data = {
        'job_link': 'https://example.com/testjob',
        'applied_on': '2023-02-25',
        'last_update_on': '2023-02-25',
        'status': 'applied'
    }
    response = logged_in_client.post('/add_job_application', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Job application added successfully!" in response.data
    
    # Check if the application appears on the tracker page
    tracker_response = logged_in_client.get('/application_tracker')
    assert b"https://example.com/testjob" in tracker_response.data

#12. Test searching candidates
def test_search_candidates_page(client, test_user):
    # Create a recruiter user
    recruiter = User(username="recruiter", email="recruiter@example.com", 
                    password="testpass12345!", is_recruiter=True)
    db.session.add(recruiter)
    db.session.commit()
    
    # Log in as the recruiter
    with client.session_transaction() as session:
        session['_user_id'] = recruiter.id
    
    # Test accessing the search candidates page
    response = client.get('/search_candidates')
    assert response.status_code == 200
    assert b"Search Candidates" in response.data

# 13. Test deleting a non-existent review
def test_delete_non_existent_review(logged_in_client):
    response = logged_in_client.post('/delete_review/9999', follow_redirects=True)
    assert response.status_code == 404 

#14. Test creating multiple reviews
def test_review_pagination(client):
    # Create multiple reviews to test pagination
    for i in range(10):
        user = User(username=f"user{i}", email=f"user{i}@example.com", password="password")
        db.session.add(user)
        db.session.commit()
        
        review = Reviews(
            job_title=f"Job Title {i}",
            job_description="Description",
            department="Department",
            locations="Location",
            hourly_pay="20",
            benefits="Benefits",
            review=f"Review content {i}",
            rating=4,
            recommendation="Yes",
            author=user
        )
        db.session.add(review)
    db.session.commit()
    
    # Test first page
    response = client.get('/review/all?page=1')
    assert response.status_code == 200
    
    # Test second page
    response = client.get('/review/all?page=2')
    assert response.status_code == 200
    
    # The content on different pages should be different
    assert response.data != client.get('/review/all?page=1').data

#15. Test review creation
def test_page_content_post_filtering(client):
    # Create some reviews with different titles and locations
    user = User(username="filteruser", email="filter@example.com", password="password")
    db.session.add(user)
    db.session.commit()
    
    review1 = Reviews(
        job_title="Frontend Developer",
        job_description="Test Description",
        department="Engineering",
        locations="New York",
        hourly_pay="25",
        benefits="Health Insurance",
        review="Good job",
        rating=4,
        recommendation="Yes",
        author=user
    )
    
    review2 = Reviews(
        job_title="Backend Developer",
        job_description="Test Description",
        department="Engineering",
        locations="San Francisco",
        hourly_pay="30",
        benefits="Health Insurance",
        review="Great job",
        rating=5,
        recommendation="Yes",
        author=user
    )
    
    db.session.add_all([review1, review2])
    db.session.commit()
    
    # Test filtering by title
    response = client.post('/pageContentPost', data={
        'search_title': 'Frontend',
        'search_location': '',
        'min_rating': 1,
        'max_rating': 5
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Frontend Developer" in response.data
    assert b"Backend Developer" not in response.data

#16. Test logging in already logged in 
def test_login_when_already_logged_in(logged_in_client):
    response = logged_in_client.get('/login')
    # Should redirect to homepage if already logged in
    assert response.status_code == 302
    
    # Follow the redirect
    response = logged_in_client.get('/login', follow_redirects=True)
    assert response.status_code == 200
    # Should have been redirected to the home page
    assert b"NC State Campus Jobs" in response.data or b"Home" in response.data

#17. Test loading home page
def test_home_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"NC State Campus Jobs" in response.data or b"Home" in response.data

# 18. Test login page access
def test_login_page_access(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data or b"Sign In" in response.data

# 19. Test access to dashboard
def test_dashboard_access(logged_in_client):
    response = logged_in_client.get('/dashboard')
    assert response.status_code == 200
    # Check for some expected content
    assert b"Jobs" in response.data or b"Dashboard" in response.data

# 20. Test update job application status
def test_update_job_application_status(logged_in_client):
    # First create a job application
    data = {
        'job_link': 'https://example.com/job123',
        'applied_on': '2023-02-25',
        'last_update_on': '2023-02-25',
        'status': 'applied'
    }
    logged_in_client.post('/add_job_application', data=data, follow_redirects=True)
    
    # Get the application ID
    application = JobApplication.query.filter_by(job_link='https://example.com/job123').first()
    
    # Update the status
    update_data = {'status': 'interview'}
    response = logged_in_client.post(f'/update_status/{application.id}', 
                                    data=update_data, 
                                    follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Application status updated successfully" in response.data

#21. Test accessing review page
def test_review_page_access(client):
    # Create a review first
    user = User(username="reviewuser", email="review@example.com", password="password")
    db.session.add(user)
    db.session.commit()
    
    review = Reviews(
        job_title="Test Job",
        job_description="Test Description",
        department="Test Department",
        locations="Test Location",
        hourly_pay="20",
        benefits="Test Benefits",
        review="Test Review",
        rating=4,
        recommendation="Yes",
        author=user
    )
    db.session.add(review)
    db.session.commit()
    
    # Test accessing the review page
    response = client.get(f'/review/{review.id}')
    assert response.status_code == 200
    assert b"Test Job" in response.data
    assert b"Test Review" in response.data

#22. Test accessing review page
def test_upvote_review(logged_in_client):
    # Create a review first
    user = User(username="upvoteuser", email="upvote@example.com", password="password")
    db.session.add(user)
    db.session.commit()
    
    review = Reviews(
        job_title="Upvote Test Job",
        job_description="Test Description",
        department="Test Department",
        locations="Test Location",
        hourly_pay="20",
        benefits="Test Benefits",
        review="Test Review",
        rating=4,
        recommendation="Yes",
        upvotes=0,
        author=user
    )
    db.session.add(review)
    db.session.commit()
    
    # Set the referer header to avoid redirect issues
    headers = {'Referer': '/review/all'}
    
    # Test upvoting the review
    response = logged_in_client.post(f'/upvote/{review.id}', headers=headers, follow_redirects=True)
    assert response.status_code == 200
    
    # Check if the upvote was registered
    updated_review = Reviews.query.get(review.id)
    assert updated_review.upvotes == 1


##############################################
##############################################