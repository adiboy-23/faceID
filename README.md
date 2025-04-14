# Face ID Login System

A Django web application that implements facial recognition for user authentication and hotel booking management.

## Features

- User registration with facial recognition
- Face ID login system
- Hotel booking information management
- User profile dashboard
- Account deletion functionality

## Requirements

- Python 3.8+
- Django 5.2
- face_recognition library
- Pillow
- Modern web browser with camera access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd FaceIDLoginSystem
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Usage

1. Register a new account:
   - Visit `/register/`
   - Fill in your details
   - Allow camera access
   - Capture your face photo
   - Submit the form

2. Login with Face ID:
   - Visit `/login/`
   - Enter your username
   - Allow camera access
   - Look at the camera
   - The system will verify your face and log you in

3. View Dashboard:
   - After successful login, you'll be redirected to your dashboard
   - View your profile photo and booking information
   - Option to delete your account

## Security Notes

- The system uses Django's built-in security features
- Face recognition is performed server-side
- All sensitive data is stored securely
- CSRF protection is enabled
- Session management is handled by Django

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 