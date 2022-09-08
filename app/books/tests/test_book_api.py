import tempfile
import os

from PIL import Image

from email.policy import default
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework import test
from rest_framework.test import APIClient

from core.models import Book, Genre, Tag

from books.serializers import BookSerializer, BookDetailSerializer


BOOKS_URLS = reverse('books:book-list')


def image_upload_url(book_id):
    """Return URL for the book image upload"""
    return reverse('books:book-upload-image', args=[book_id])

def detail_url(book_id):
    """Return book detail URL"""
    return reverse('books:book-detail', args=[book_id])

def sample_tag(user, name='Story'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)

def sample_genre(user, name='Thriller'):
    """Create and return a sample genre"""
    return Genre.objects.create(user=user, name=name)

def sample_book(user, **params):
    """Create and return a simple book"""
    defaults = {
        'title': 'God Help Me',
        'author': 'Bikash Poudel',
        'price': 6.19,
        'quantity': 2
    }
    defaults.update(params)

    return Book.objects.create(user=user, **defaults)


class PublicBookApiTests(TestCase):
    """Test unauthenticated book API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(BOOKS_URLS)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookApiTest(TestCase):
    """Test unauthenticated book API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'bikashpoudel4@gmail.com',
            'okmygvijn'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_books(self):
        """Test retrieving list of books"""
        sample_book(user=self.user)
        sample_book(user=self.user)

        res = self.client.get(BOOKS_URLS)

        books = Book.objects.all().order_by('-id')
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_books_limited_to_user(self):
        """Test retrieving receipies for user"""
        user2 = get_user_model().objects.create_user(
            'bikashpoudel@gmail.com',
            'poiuytrew'
        )
        sample_book(user=user2)
        sample_book(user=self.user)
        res = self.client.get(BOOKS_URLS)

        books = Book.objects.filter(user=self.user)
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a book detail"""
        recipe = sample_book(user=self.user)
        recipe.tag.add(sample_tag(user=self.user))
        recipe.genre.add(sample_genre(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = BookDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
    
    def test_create_basic_book(self):
        """Test creating book"""
        payload = {
            'title': 'God House',
            'author': 'Bikash Poudel',
            'price': 15.00,
            'quantity' : 25
        }
        res = self.client.post(BOOKS_URLS, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data['id'])
        for key in payload.keys():
            """Look through each key in dict"""
            self.assertEqual(payload[key], getattr(book, key))

    def test_create_book_with_tags(self):
        """Test creating a book with tags"""
        tag1 = sample_tag(user=self.user, name='paradise')
        tag2 = sample_tag(user=self.user, name='life')
        payload = {
            'title': 'God House2',
            'author': 'Bikash Poudel',
            'price': 10.10,
            'quantity' : 5,
            'tag': [tag1.id, tag2.id]
        }
        res = self.client.post(BOOKS_URLS, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data['id'])
        tag = book.tag.all()
        self.assertEqual(tag.count(), 2)
        self.assertIn(tag1, tag)
        self.assertIn(tag2, tag)
    
    def test_create_book_with_genre(self):
        """"Test creating book with genre"""
        genre1 = sample_genre(user=self.user, name='comic')
        genre2 = sample_genre(user=self.user, name='scientific')
        payload = {
            'title': 'God House2',
            'author': 'Bikash Poudel',
            'price': 11.10,
            'quantity' : 5,
            'genre': [genre1.id, genre2.id]
        }
    
        res = self.client.post(BOOKS_URLS, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data['id'])
        genre = book.genre.all()
        self.assertEqual(genre.count(), 2)
        self.assertIn(genre1, genre)
        self.assertIn(genre2, genre)

    def test_partial_update_book(self):
        """Test updating book with patch"""
        book = sample_book(user=self.user)
        book.tag.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Photography')

        payload = {
            'title': 'God in Mind',
            'tags': [new_tag.id]
        }
        url = detail_url(book.id)
        self.client.patch(url, payload)

        book.refresh_from_db()
        self.assertEqual(book.title, payload['title'])
        tag = book.tag.all()
        self.assertEqual(len(tag), 1)

    def test_full_update_book(self):
        """Test updating a book with put"""
        book = sample_book(user=self.user)
        book.tag.add(sample_tag(user=self.user))
        payload = {
            'title': 'Astrology',
            'author': 'Calvin',
            'price': 6.00,
            'quantity': 10
        }
        url = detail_url(book.id)
        self.client.put(url, payload)

        book.refresh_from_db()
        self.assertEqual(book.title, payload['title'])
        self.assertEqual(book.author, payload['author'])
        self.assertEqual(book.price, payload['price'])
        # self.assertAlmostEqual(book.price, payload['price'])
        self.assertEqual(book.quantity, payload['quantity'])
        tag = book.tag.all()
        self.assertEqual(len(tag), 0)


class BookImageUploadTests(TestCase):
    """Image Upload test"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'bikashpoudel4@gmail.com',
            'poiuytrew'
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book(user=self.user)

    def tearDown(self):
        self.book.image.delete()

    def test_upload_image_to_book(self):
        """Test uploading an email to book"""
        url = image_upload_url(self.book.id)
        with tempfile.NamedTemporaryFile(suffix= '.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.book.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.book.id)
        res = self.client.post(url, {'image': 'noimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_book_by_tags(self):
        """Test returning book with specific tags"""
        book1 = sample_book(user=self.user, title='Mystic Mountain')
        book2 = sample_book(user=self.user, title='SAARAS')
        tag1 = sample_tag(user=self.user, name='Treking')
        tag2 = sample_tag(user=self.user, name='Photography')
        book1.tag.add(tag1)
        book2.tag.add(tag2)
        book3 = sample_book(user=self.user, title='Everest')

        res = self.client.get(
            BOOKS_URLS,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = BookSerializer(book1)
        serializer2 = BookSerializer(book2)
        serializer3 = BookSerializer(book3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_book_by_genre(self):
        """Test returning book with specific genre"""
        book1 = sample_book(user=self.user, title='Cook Book')
        book2 = sample_book(user=self.user, title='Yoga')
        genre1 = sample_genre(user=self.user, name='Food')
        genre2 = sample_genre(user=self.user, name='Fitness')
        book1.genre.add(genre1)
        book2.genre.add(genre2)
        book3 = sample_book(user=self.user, title='Impossible')

        res = self.client.get(
            BOOKS_URLS,
            {'genres': f'{genre1.id},{genre2.id}'}
        )

        serializer1 = BookSerializer(book1)
        serializer2 = BookSerializer(book2)
        serializer3 = BookSerializer(book3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

