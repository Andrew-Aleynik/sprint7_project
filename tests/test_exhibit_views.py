import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from exhibits.models import Floor, Hall, Exhibit, ExhibitImage


@pytest.fixture
def floor(db):
    """Создание этажа"""
    return Floor.objects.create(number=1, name="Первый этаж")


@pytest.fixture
def hall(db, floor):
    """Создание зала"""
    return Hall.objects.create(name="Зал", floor=floor)


@pytest.fixture
def staff_user(db):
    """Создает пользователя-админа"""
    return User.objects.create_user(
        username="staff_user", password="testpass123", is_staff=True
    )


@pytest.fixture
def regular_user(db):
    """Создает обычного пользователя"""
    return User.objects.create_user(
        username="regular_user", password="testpass123", is_staff=False
    )


@pytest.fixture
def on_display_exhibit(db, hall):
    """Создает экспонат со статусом 'on_display'"""
    exhibit = Exhibit.objects.create(
        name="Видимый экспонат",
        description="Описание видимого экспоната",
        status="on_display",
        hall=hall,
    )
    # Добавляем изображения
    ExhibitImage.objects.create(exhibit=exhibit, image="test_image1.jpg")
    ExhibitImage.objects.create(exhibit=exhibit, image="test_image2.jpg")
    return exhibit


@pytest.fixture
def archived_exhibit(db, hall):
    """Создает экспонат со статусом 'archived'"""
    return Exhibit.objects.create(
        name="Архивный экспонат",
        description="Описание архивного экспоната",
        status="sent_to_storage",  # или "archived", если такое поле есть
        hall=hall,
    )


@pytest.fixture
def multiple_exhibits(db, hall):
    """Создает несколько экспонатов с разными статусами"""
    exhibits = []
    for i in range(3):
        status = "on_display" if i % 2 == 0 else "sent_to_storage"
        exhibit = Exhibit.objects.create(
            name=f"Экспонат {i}",
            description=f"Описание {i}",
            status=status,
            hall=hall,
        )
        exhibits.append(exhibit)
    return exhibits


class TestExhibitListView:
    """Тесты для exhibit_list"""

    @pytest.mark.django_db
    def test_url_exists_at_desired_location(self, client):
        """Тест доступности URL"""
        response = client.get("/")
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_url_accessible_by_name(self, client):
        """Тест доступности по имени URL"""
        response = client.get(reverse("exhibits:exhibit_list"))
        assert response.status_code == 200

    def test_view_uses_correct_template(self, client, on_display_exhibit):
        """Тест используемого шаблона"""
        response = client.get(reverse("exhibits:exhibit_list"))
        assert response.status_code == 200
        assert "exhibits/exhibit_list.html" in [t.name for t in response.templates]

    def test_context_contains_exhibits(self, client, on_display_exhibit):
        """Тест контекста с экспонатами"""
        response = client.get(reverse("exhibits:exhibit_list"))
        assert "exhibits" in response.context
        assert len(response.context["exhibits"]) == 1
        assert response.context["exhibits"][0] == on_display_exhibit

    def test_only_on_display_exhibits_are_shown(self, client, multiple_exhibits):
        """Тест отображения только экспонатов со статусом 'on_display'"""
        response = client.get(reverse("exhibits:exhibit_list"))
        exhibits = response.context["exhibits"]

        # Должны быть только экспонаты со статусом 'on_display'
        assert len(exhibits) == 2  # из 3 созданных, 2 с on_display
        for exhibit in exhibits:
            assert exhibit.status == "on_display"

    @pytest.mark.django_db
    def test_empty_list(self, client):
        """Тест пустого списка экспонатов"""
        response = client.get(reverse("exhibits:exhibit_list"))
        assert response.status_code == 200
        assert len(response.context["exhibits"]) == 0


class TestExhibitDetailView:
    """Тесты для exhibit_detail"""

    def test_url_exists_at_desired_location(self, client, on_display_exhibit):
        """Тест доступности URL"""
        response = client.get(f"/{on_display_exhibit.pk}/")
        assert response.status_code == 200

    def test_url_accessible_by_name(self, client, on_display_exhibit):
        """Тест доступности по имени URL"""
        url = reverse("exhibits:exhibit_detail", kwargs={"pk": on_display_exhibit.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_view_uses_correct_template(self, client, on_display_exhibit):
        """Тест используемого шаблона"""
        url = reverse("exhibits:exhibit_detail", kwargs={"pk": on_display_exhibit.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert "exhibits/exhibit_detail.html" in [t.name for t in response.templates]

    def test_context_contains_exhibit(self, client, on_display_exhibit):
        """Тест контекста с экспонатом"""
        url = reverse("exhibits:exhibit_detail", kwargs={"pk": on_display_exhibit.pk})
        response = client.get(url)
        assert "exhibit" in response.context
        assert response.context["exhibit"] == on_display_exhibit

    def test_regular_user_can_view_on_display_exhibit(
        self, client, on_display_exhibit, regular_user
    ):
        """Тест: обычный пользователь видит экспонат on_display"""
        client.force_login(regular_user)
        url = reverse("exhibits:exhibit_detail", kwargs={"pk": on_display_exhibit.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_anonymous_user_can_view_on_display_exhibit(
        self, client, on_display_exhibit
    ):
        """Тест: анонимный пользователь видит экспонат on_display"""
        url = reverse("exhibits:exhibit_detail", kwargs={"pk": on_display_exhibit.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_staff_user_can_view_archived_exhibit(
        self, client, archived_exhibit, staff_user
    ):
        """Тест: сотрудник видит архивный экспонат"""
        client.force_login(staff_user)
        url = reverse("exhibits:exhibit_detail", kwargs={"pk": archived_exhibit.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_regular_user_cannot_view_archived_exhibit(
        self, client, archived_exhibit, regular_user
    ):
        """Тест: обычный пользователь НЕ видит архивный экспонат"""
        client.force_login(regular_user)
        url = reverse("exhibits:exhibit_detail", kwargs={"pk": archived_exhibit.pk})
        response = client.get(url)
        assert response.status_code == 404

    def test_anonymous_user_cannot_view_archived_exhibit(
        self, client, archived_exhibit
    ):
        """Тест: анонимный пользователь НЕ видит архивный экспонат"""
        url = reverse("exhibits:exhibit_detail", kwargs={"pk": archived_exhibit.pk})
        response = client.get(url)
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_nonexistent_exhibit_returns_404(self, client):
        """Тест несуществующего экспоната"""
        url = reverse("exhibits:exhibit_detail", kwargs={"pk": 999})
        response = client.get(url)
        assert response.status_code == 404
