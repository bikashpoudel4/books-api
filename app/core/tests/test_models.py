from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='abc@xyz.com', password='poiuytrew'):
    """Creating sample user"""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'abc@test.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@ABCD.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())


    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    
    def test_create_new_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@abcd.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='adventure'
        )

        self.assertEqual(str(tag), tag.name)

    def test_genre_str(self):
        """Test the genre string representation"""
        genre = models.Genre.objects.create(
            user = sample_user(),
            name = 'Dark'
        )

        self.assertEqual(str(genre), genre.name)

    def test_books_str(self):
        """Test the book string representation"""
        books = models.Book.objects.create(
            user=sample_user(),
            title = 'God Help Me',
            author = 'Bikash Poudel',
            price = 30.10,
            quantity = 8
        )

        self.assertEqual(str(books), books.title)

    @patch('uuid.uuid4')
    def test_book_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.book_image_file_path(None, 'action.jpg')

        exp_path = f'uploads/books/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)