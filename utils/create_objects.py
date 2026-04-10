import os
import sys
from pathlib import Path
import random
from list_items import objects
import faker
from faker.providers import BaseProvider
import django
from django.conf import settings

DJANGO_BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(DJANGO_BASE_DIR))
os.environ["DJANGO_SETTINGS_MODULE"] = "project.settings"
django.setup()

settings.USE_TZ = False

if __name__ == "__main__":

    from storage.models import Item, User, Transaction

    Item.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    Transaction.objects.all().delete()

    fake = faker.Faker("pt-br")

    class StorageProvider(BaseProvider):
        """
        Custom Faker provider for generating storage-specific data.

        Methods
        -------
        random_object_name()
            Returns a random object name from the imported objects list.
        random_storage_location()
            Returns a random physical location from a predefined list.
        """

        def random_object_name(self):
            """Returns a random item name from the objects dataset."""
            return self.random_element(objects)

        def random_storage_location(self):
            """Returns a random storage area string."""
            local = ["Armazem", "Pátio 1", "Pátio 2", "Pátio 3"]
            return self.random_element(local)

    fake.add_provider(StorageProvider)

    def generate_data(NUMBER_OF_USERS=150, ITEMS_PER_USER=40):
        """
        Generates and persists mock data for Users and Items.

        This function creates a set number of users and, for each user,
        creates a specified number of Item instances. It uses bulk_create
        for optimized database insertion of Item objects.

        Parameters
        ----------
        NUMBER_OF_USERS : int, optional
            The number of User accounts to create (default is 150).
        ITEMS_PER_USER : int, optional
            The number of Item objects to assign to each created user (default is 40).
        """
        django_storage = []

        for _ in range(NUMBER_OF_USERS):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                password="password123",
            )

            for _ in range(ITEMS_PER_USER):
                django_storage.append(
                    Item(
                        object=fake.random_object_name(),
                        description=fake.text(max_nb_chars=70),
                        quantity=random.randint(1, 10),
                        storage_location=fake.random_storage_location(),
                        is_available=bool(random.getrandbits(1)),
                        created_date=fake.date_this_year(),
                        owner=user,
                    )
                )

        if django_storage:
            Item.objects.bulk_create(django_storage)
            print(
                f"Sucesso: {len(django_storage)} itens criados para {NUMBER_OF_USERS} usuários."
            )

    generate_data()
