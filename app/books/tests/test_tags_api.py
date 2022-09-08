from genericpath import exists
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, tag

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Book

from books.serializers import TagSerializer


TAGS_URL = reverse('books:tag-list')

class PublicTagsApiTests(TestCase):
    """Test the publicaly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tag"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testtest'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tset_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Adventure')
        Tag.objects.create(user=self.user, name='Mythology')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""

        user2 = get_user_model().objects.create_user(
            'cde@bnx.com',
            'poiuytrew'
        )
        Tag.objects.create(user=user2, name='Discovery')
        tag = Tag.objects.create(user=self.user, name='Culture')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
    
    def test_create_tag_successful(self):
        """test creating a new tag"""
        payload = {'name': 'Test tags'}
        self.client.post(TAGS_URL,payload)

        exists = Tag.objects.filter(
            user = self.user,
            name = payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrieve_tag_assigned_to_books(self):
        """Test filtering tags by those assigned to books"""
        tag1 = Tag.objects.create(user=self.user, name='fitness')
        tag2 = Tag.objects.create(user=self.user, name='religion')
        book = Book.objects.create(
            title = 'Positiveness',
            author = 'Bikash Poudel',
            price = 20.00,
            quantity = 1,
            user=self.user
        )
        book.tag.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """TEST filtering tags by assigned returns unique items"""
        tag =Tag.objects.create(user=self.user, name='Motivational')
        Tag.objects.create(user=self.user, name='Thinking')
        book1 = Book.objects.create(
            title = 'Faith',
            author = 'John',
            price = 21.00,
            quantity = 2,
            user=self.user
        )
        book1.tag.add(tag)
        book2 = Book.objects.create(
            title = 'The impossible',
            author = 'Nims Dai',
            price = 21.00,
            quantity = 10,
            user=self.user
        )
        book2.tag.add(tag)

        res =  self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

