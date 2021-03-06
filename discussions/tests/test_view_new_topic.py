from django.urls import reverse, resolve
from django.test import TestCase
from django.contrib.auth.models import User
from ..views import new_topic #metodinkin voi näin tuoda.
from ..models import Discussion, Topic, Post
from ..forms import NewTopicForm

class NewTopicsTestsNotLoggedIn(TestCase):
    def setUp(self):
        Discussion.objects.create(name='Django', description='Django discussion')

    def test_new_topic_view_status_and_redirect_id_ok(self):
        url_ok_id = reverse('url_new_topic', kwargs={'discussion_id': 1})
        response_ok_id = self.client.get(url_ok_id)
        view_ok_id = resolve('/discussions/1/new/')
        self.assertEquals(response_ok_id.status_code, 302)
        #self.assertEquals(view_ok_id.func, LoginView)

    def test_new_topic_view_status_and_redirect_id_bad(self):
        url_bad_id = reverse('url_new_topic', kwargs={'discussion_id': 99})
        response_bad_id = self.client.get(url_bad_id)
        view_bad_id = resolve('/discussions/99/new/')
        self.assertEquals(response_bad_id.status_code, 302)
        #self.assertEquals(view_bad_id.func, LoginView)

class NewTopicTestsLoginRequired(TestCase):
    def setUp(self):
        Discussion.objects.create(name='Django', description='Django discussion')
        self.url = reverse('url_new_topic', kwargs={'discussion_id': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('url_login')
        self.assertRedirects(self.response,
            '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class NewTopicsTestsLoggedIn(TestCase):
    def setUp(self):
        Discussion.objects.create(name='Django', description='Django discussion')
        self.user = User.objects.create_user(
            username='john', email='john@doe.com', password='123')

        # This makes self.client login with the user credentials:
        # Note: Just login() does not work here.
        self.client.force_login(self.user)

    def test_new_topic_view_success_status_code(self):
        url = reverse('url_new_topic', kwargs={'discussion_id': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_new_topic_view_not_found_status_code(self):
        url = reverse('url_new_topic', kwargs={'discussion_id': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_url_resolves_new_topic_view(self):
        view = resolve('/discussions/1/new/')
        self.assertEquals(view.func, new_topic)

    def test_new_topic_view_contains_links(self):
        url = reverse('url_new_topic', kwargs={'discussion_id':1})
        response = self.client.get(url)
        home_url = reverse('url_home')
        topics_url = reverse('url_discussion_topics', kwargs={'discussion_id':1})

        # {0} refers to the 1st param of format function.
        self.assertContains(response, 'href="{0}"'.format(home_url))
        self.assertContains(response, 'href="{0}"'.format(topics_url))

    def test_csrf(self):
        url = reverse('url_new_topic', kwargs={'discussion_id': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        url = reverse('url_new_topic', kwargs={'discussion_id': 1})
        data = {
            'subject': 'Test title',
            'message': 'Lorem ipsum dolor sit amet'
        }
        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('url_new_topic', kwargs={'discussion_id': 1})
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 200)

    def test_new_topic_invalid_post_data_empty_fields(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('url_new_topic', kwargs={'discussion_id': 1})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

    def test_contains_form(self):  # <- new test
        url = reverse('url_new_topic', kwargs={'discussion_id': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_invalid_post_data(self):  # <- updated this one
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('url_new_topic', kwargs={'discussion_id': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
