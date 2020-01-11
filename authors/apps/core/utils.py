import random
import string
from django.utils.text import slugify

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_slug(title, max=255):
    """
    Create a slug from the title
    """
    slug = slugify(title)
    unique = random_string_generator()

    slug = slug[:max]
    while len(slug + '-' + unique) > max:
        parts = slug.split('-')

        if len(parts) is 1:
            slug = slug[:max - len(unique) - 1]
        else:
            slug = '-'.join(parts[:-1])

    return slug + '-' + unique
