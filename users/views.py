from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import UserProfile
from django.contrib.auth.models import User
import base64
import os
from django.conf import settings
import json
from datetime import datetime
from django.core.files.base import ContentFile
import traceback
import logging

# Set up logging
logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        try:
            logger.info("Starting registration process")
            data = json.loads(request.body)
            logger.info(f"Received data: {data.keys()}")
            
            username = data.get('username')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            passport_number = data.get('passport_number')
            date_of_birth = data.get('date_of_birth')
            hotel_name = data.get('hotel_name')
            room_number = data.get('room_number')
            check_in_date = data.get('check_in_date')
            check_out_date = data.get('check_out_date')
            face_image_data = data.get('face_image')
            
            logger.info(f"Username: {username}, First Name: {first_name}, Last Name: {last_name}")

            # Validate required fields
            if not all([username, password, first_name, last_name, passport_number, 
                       date_of_birth, hotel_name, room_number, check_in_date, check_out_date]):
                logger.error("Missing required fields")
                return JsonResponse({'error': 'All fields are required'}, status=400)

            if User.objects.filter(username=username).exists():
                logger.warning(f"Username already exists: {username}")
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # Create user
            logger.info("Creating user")
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            logger.info(f"User created: {user.username}")

            # Save face image
            logger.info("Processing face image")
            if not face_image_data:
                logger.error("No face image data provided")
                return JsonResponse({'error': 'No face image provided'}, status=400)
                
            try:
                face_image_data = face_image_data.split(',')[1]
                face_image_bytes = base64.b64decode(face_image_data)
                logger.info(f"Face image decoded, size: {len(face_image_bytes)} bytes")
            except Exception as e:
                logger.error(f"Error processing face image data: {str(e)}")
                return JsonResponse({'error': 'Invalid face image data'}, status=400)
            
            # Create the face_images directory if it doesn't exist
            face_images_dir = os.path.join(settings.MEDIA_ROOT, 'face_images')
            logger.info(f"Creating directory: {face_images_dir}")
            os.makedirs(face_images_dir, exist_ok=True)
            
            # Create user profile with all required fields
            logger.info("Creating user profile")
            try:
                profile = UserProfile.objects.create(
                    user=user,
                    passport_number=passport_number,
                    date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date(),
                    hotel_name=hotel_name,
                    room_number=room_number,
                    check_in_date=datetime.strptime(check_in_date, '%Y-%m-%d').date(),
                    check_out_date=datetime.strptime(check_out_date, '%Y-%m-%d').date()
                )
                
                # Save the face image
                logger.info("Saving face image")
                image_name = f"{username}.jpg"
                profile.face_image.save(image_name, ContentFile(face_image_bytes), save=True)
                logger.info(f"Face image saved: {profile.face_image.path}")
                
                return JsonResponse({'message': 'Registration successful'})
            except Exception as e:
                logger.error(f"Error creating user profile: {str(e)}")
                # Clean up the user if profile creation fails
                user.delete()
                return JsonResponse({'error': f'Error creating user profile: {str(e)}'}, status=500)
                
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            logger.error(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'users/register.html')

def face_login(request):
    if request.method == 'POST':
        try:
            import face_recognition  # Import only when needed
            data = json.loads(request.body)
            username = data.get('username')
            face_image_data = data.get('face_image')

            try:
                user = User.objects.get(username=username)
                profile = user.userprofile

                # Decode and save temporary face image
                face_image_data = face_image_data.split(',')[1]
                face_image_bytes = base64.b64decode(face_image_data)
                temp_image_path = os.path.join(settings.MEDIA_ROOT, 'temp_face.jpg')
                
                with open(temp_image_path, 'wb') as f:
                    f.write(face_image_bytes)

                # Load the images
                known_image = face_recognition.load_image_file(profile.face_image.path)
                unknown_image = face_recognition.load_image_file(temp_image_path)

                # Get face encodings
                known_encodings = face_recognition.face_encodings(known_image)
                unknown_encodings = face_recognition.face_encodings(unknown_image)

                # Clean up temporary file
                os.remove(temp_image_path)

                if not known_encodings:
                    return JsonResponse({'error': 'No face detected in registered image'}, status=400)
                
                if not unknown_encodings:
                    return JsonResponse({'error': 'No face detected in login image'}, status=400)

                # Compare faces
                results = face_recognition.compare_faces([known_encodings[0]], unknown_encodings[0])

                if results[0]:
                    login(request, user)
                    return JsonResponse({'message': 'Login successful'})
                else:
                    return JsonResponse({'error': 'Face not recognized'}, status=400)

            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'users/login.html')

@login_required
def dashboard(request):
    profile = request.user.userprofile
    context = {
        'profile': profile,
        'user': request.user
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def delete_account(request):
    if request.method == 'POST':
        try:
            user = request.user
            # Delete the face image
            if user.userprofile.face_image:
                try:
                    # Get the path to the file
                    file_path = user.userprofile.face_image.path
                    # Delete the file from the filesystem
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting face image: {e}")
            
            # Delete the user (this will cascade delete the profile)
            user.delete()
            return JsonResponse({'message': 'Account deleted successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
