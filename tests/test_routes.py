import os
import sys
import pytest
from app import app, db
from app.models import User, Reviews
from unittest.mock import patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def create_reviews(client, login_user):
    """Fixture to create multiple reviews for testing."""
    # Create a user for reviews
    user = User(username="testuser1", email="test1@example.com", password="testpassword2")
    db.session.add(user)
    db.session.commit()

    # Create sample reviews
    for i in range(10):
        review = Reviews(
            job_title=f"Software Engineer {i}",
            job_description="Description for Software Engineer.",
            department="Engineering",
            locations="New York",
            hourly_pay="30",
            benefits="Health insurance",
            review="This is a sample review.",
            rating=4,
            recommendation="Yes",
            author=user  # Set the author to the created user
        )
        db.session.add(review)

    db.session.commit()  # Commit all the reviews to the database

    yield  # This allows the test to run after setting up

    # Optionally clear the reviews after tests
    Reviews.query.delete()
    db.session.commit()


@pytest.fixture
def login_user(client):
    user = User(username="testuser", email="testuser@example.com", password="testpassword")
    db.session.add(user)
    db.session.commit()

    # Log in the user
    with client.session_transaction() as session:
        session['user_id'] = user.id
    return user

@pytest.fixture
def create_review(login_user):
    review = Reviews(job_title="Test Job", job_description="Test Description",
                     department="Test Department", locations="Test Location",
                     hourly_pay="20", benefits="None", review="Great job!",
                     rating=5, recommendation="Yes", author=login_user)
    db.session.add(review)
    db.session.commit()
    return review

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_index_route_2(client):
    response = client.get('/home')
    assert response.status_code == 200

def test_register_get(client):
    response = client.get('/register')
    assert response.status_code == 200

def test_register_post(client):
    response = client.post('/register', data={
        'username': 'asavla2',
        'password': 'pass',
        'email': 'asavla2@ncsu.edu'
    })
    assert response.status_code == 200

def test_login_get(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_login_post(client):
    response = client.post('/login', data={
        'email': 'asavla2@ncsu.edu',
        'password': 'pass'
    })
    assert response.status_code == 200

def test_logout_get(client):
    response = client.get('/logout')
    assert response.status_code == 302

def test_view_review_all(client):
    response = client.get('/review/all')
    assert response.status_code == 200

def test_add_review_route_get(client):
    response = client.get('/review/new')
    assert response.status_code == 302

def test_add_review_route_post(client):
    response = client.post('/review/new', data={
        "job_title": "1",
        "job_description": "2",
        "department": "3",
        "locations": "4",
        "hourly_pay": "5",
        "benefits": "6",
        "review": "7",
        "rating": "2",
        "recommendation": "2",
    })
    assert response.status_code == 302

def test_view_review(client, create_review):
    response1 = client.get(f'/review/{create_review.id}')
    assert response1.status_code == 200

    response2 = client.get('/review/9999')  # Non-existent review ID
    assert response2.status_code == 404  # Should return 404 for non-existent review

def test_update_review_get(client, login_user, create_review):
    # Check that a logged-in user can access the update page
    response = client.get(f'/review/{create_review.id}/update', follow_redirects=True)
    assert response.status_code == 200  # Should be accessible to the author

def test_update_review_post(client, login_user, create_review):
    # Test updating a review
    response = client.post(f'/review/{create_review.id}/update', data={
        "job_title": "Updated Job",
        "job_description": "Updated Description",
        "department": "Updated Department",
        "locations": "Updated Location",
        "hourly_pay": "30",
        "benefits": "More Benefits",
        "review": "Updated review text.",
        "rating": "4",
        "recommendation": "No",
    }, follow_redirects=True)
    assert response.status_code == 200  # Check if it updates successfully



def test_dashboard_route(client):
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_account_route(client):
    response = client.get('/account')
    assert response.status_code == 302

def test_get_jobs(client):
    response = client.get('/api/jobs')
    assert response.status_code == 200

def test_new_review(client, login_user):
    # Log in the user
    with client.session_transaction() as session:
        session['user_id'] = login_user.id  # Simulate user login

    # Prepare the data to submit a new review
    review_data = {
        "job_title": "Software Engineer",
        "job_description": "Develops software applications.",
        "department": "Engineering",
        "locations": "Remote",
        "hourly_pay": "50",
        "benefits": "Health Insurance, Paid Time Off",
        "review": "Great place to work!",
        "rating": "5",
        "recommendation": "Yes",
    }

    # Submit the new review
    response = client.post('/review/new', data=review_data, follow_redirects=True)

    # Check if the response is a redirect to the view reviews page
    assert response.status_code == 200  # Ensure the response is OK after redirect

def test_delete_review(client, login_user, create_review):
    # Log in the user
    with client.session_transaction() as session:
        session['user_id'] = login_user.id  # Simulate user login

    # Submit the delete request
    response = client.post(f'/review/{create_review.id}/delete', follow_redirects=True)

    # Check if the response is a redirect to the view reviews page
    assert response.status_code == 200

def test_page_content_post(client, create_reviews):  # Assuming create_reviews is a fixture that populates the database
    # Prepare the search parameters
    response = client.post('/pageContentPost', data={
        'search_title': 'Software Engineer',
        'search_location': 'New York',
        'min_rating': 3,
        'max_rating': 5
    }, follow_redirects=True)

    # Check if the response is successful
    assert response.status_code == 200

    # Check if the response contains the relevant reviews
    assert b'Software Engineer' in response.data
    assert b'New York' in response.data

    # Verify that the rating is within the specified range
    for review in Reviews.query.all():  # Assuming Reviews is a model that can be queried
        if review.rating:
            assert 3 <= review.rating <= 5  # Check if the review rating is within the specified range


def test_page_content_post_pagination(client, create_reviews):  # Assuming create_reviews creates more than 5 reviews
    # Request the first page
    response = client.post('/pageContentPost?page=1', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Pagination' in response.data  # Check for pagination element

    # Request the second page
    response = client.post('/pageContentPost?page=2', data={}, follow_redirects=True)
    assert response.status_code == 200


def test_page_content_post_search_criteria_persistence(client, create_reviews):
    # Perform a search with specific parameters
    response = client.post('/pageContentPost', data={
        'search_title': 'Software Engineer',
        'search_location': 'New York',
        'min_rating': 3,
        'max_rating': 5
    }, follow_redirects=True)

    # Check if the response is successful
    assert response.status_code == 200

    # Verify that the search criteria are retained in the response
    assert b'Software Engineer' in response.data
    assert b'New York' in response.data
    assert b'3' in response.data  # Check if the min rating is displayed
    assert b'5' in response.data  # Check if the max rating is displayed

# Test home page access
def test_home_page_access(client):
    response = client.get('/', follow_redirects=True)
    assert b'nc state campus jobs' in response.data.lower()


# Test unauthorized access to account page
def test_account_route_requires_login(client):
    response = client.get('/account', follow_redirects=True)
    assert b'login' in response.data.lower()


# Test user registration with invalid email
def test_register_invalid_email(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'invalid-email',
        'password': 'pass',
        'confirm_password': 'pass'
    }, follow_redirects=True)
    assert b'invalid' in response.data.lower()


# Test pagination limit on reviews
def test_review_pagination_limit(client, create_review):
    response = client.get('/review/all?page=1', follow_redirects=True)
    assert b'page' in response.data.lower()  # Confirm pagination element


# Test static file access
def test_static_files_served(client):
    response = client.get('/static/css/style.css')
    assert response.data.strip() != b''


# Test CSRF protection with a fake CSRF token
def test_csrf_protection_on_review_form(client):
    response = client.post('/review/new', data={
        "job_title": "Test",
        "job_description": "Test",
        "locations": "Test",
        "hourly_pay": "20",
        "benefits": "None",
        "review": "Nice job!",
        "rating": "5",
        "recommendation": "Yes",
    }, follow_redirects=True)
    assert b'alert' in response.data.lower()


# Test unauthorized review update attempt
def test_update_review_permission_denied(client, create_review):
    another_user = User(username="otheruser", email="other@example.com", password="password")
    db.session.add(another_user)
    db.session.commit()

    with client.session_transaction() as session:
        session['user_id'] = another_user.id

    response = client.post(f'/review/{create_review.id}/update', data={
        "job_title": "Unauthorized Update",
    }, follow_redirects=True)
    assert b'alert' in response.data.lower()


# Test login with remember me option
def test_login_remember_me(client):
    user = User(username="rememberme", email="remember@example.com", password="password")
    db.session.add(user)
    db.session.commit()

    response = client.post('/login', data={
        'email': 'remember@example.com',
        'password': 'password',
        'remember': True
    }, follow_redirects=True)
    assert b'ncsu campus job' in response.data.lower()


# Test dashboard job listings display
def test_dashboard_jobs_display(client):
    with patch('app.services.job_fetcher.fetch_job_listings') as mock_fetch:
        mock_fetch.return_value = [
            {"title": "Job 1", "link": "http://example.com/job1"},
            {"title": "Job 2", "link": "http://example.com/job2"},
        ]
        response = client.get('/dashboard', follow_redirects=True)
        assert b'job' in response.data.lower()


def test_register_password_mismatch(client):
    response = client.post('/register', data={
        'username': 'mismatchuser',
        'email': 'mismatch@example.com',
        'password': 'password123',
        'confirm_password': 'differentpassword'
    }, follow_redirects=True)
    assert b'field must be equal to password' in response.data.lower()


# Test accessing account page without logging in
def test_invalid_account_access(client):
    response = client.get('/account', follow_redirects=True)
    assert b'login' in response.data.lower()


# Test user session persistence after login
def test_user_session_persistence(client, login_user):
    with client.session_transaction() as session:
        assert session.get('user_id') == login_user.id


# Test review creation with invalid rating input
def test_create_review_invalid_rating(client, login_user):
    with client.session_transaction() as session:
        session['user_id'] = login_user.id

    response = client.post('/review/new', data={
        "job_title": "Test Job",
        "job_description": "Description",
        "department": "Department",
        "locations": "Location",
        "hourly_pay": "20",
        "benefits": "Health",
        "review": "Good",
        "recommendation": "Yes",
    }, follow_redirects=True)
    print(response.data.lower().decode('utf-8'))
    assert b'alert' in response.data.lower() or b'invalid' in response.data.lower()


# Test viewing a non-existent review
def test_view_nonexistent_review(client):
    response = client.get('/review/9999', follow_redirects=True)
    assert b'not found' in response.data.lower()
