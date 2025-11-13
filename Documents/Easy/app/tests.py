# ...existing code...
from types import SimpleNamespace
from django.test import TestCase
from django.template import Template, Context

class TemplateLogicTests(TestCase):
    def test_damage_indicator_shows_fee_when_reported(self):
        tpl = Template(
            '{% if booking.damage_reported %}Damage Reported - Fee: ₹{{ booking.damage_fee|floatformat:2 }}{% else %}No Damage{% endif %}'
        )
        booking = SimpleNamespace(damage_reported=True, damage_fee=123.45)
        rendered = tpl.render(Context({'booking': booking}))
        self.assertIn('Damage Reported - Fee: ₹123.45', rendered)

    def test_damage_indicator_shows_no_damage_when_not_reported(self):
        tpl = Template(
            '{% if booking.damage_reported %}Damage Reported - Fee: ₹{{ booking.damage_fee|floatformat:2 }}{% else %}No Damage{% endif %}'
        )
        booking = SimpleNamespace(damage_reported=False, damage_fee=0)
        rendered = tpl.render(Context({'booking': booking}))
        self.assertIn('No Damage', rendered)

    def test_driver_image_check_uses_fallback_when_missing(self):
        tpl = Template(
            '{% if driver.image %}HAS_IMG:{{ driver.image.url }}{% else %}NO_IMG{% endif %}'
        )
        # case: no image
        driver_no_img = SimpleNamespace(image=None, name='Alice')
        rendered_no = tpl.render(Context({'driver': driver_no_img}))
        self.assertIn('NO_IMG', rendered_no)

        # case: has image-like object with .url
        img_obj = SimpleNamespace(url='/media/drivers/alice.jpg')
        driver_with_img = SimpleNamespace(image=img_obj, name='Alice')
        rendered_yes = tpl.render(Context({'driver': driver_with_img}))
        self.assertIn('HAS_IMG:/media/drivers/alice.jpg', rendered_yes)
# ...existing code...
# filepath: /home/rguktrkvalley/Documents/Easy/app/tests.py
# ...existing code...
from types import SimpleNamespace
from django.test import TestCase
from django.template import Template, Context

class TemplateLogicTests(TestCase):
    def test_damage_indicator_shows_fee_when_reported(self):
        tpl = Template(
            '{% if booking.damage_reported %}Damage Reported - Fee: ₹{{ booking.damage_fee|floatformat:2 }}{% else %}No Damage{% endif %}'
        )
        booking = SimpleNamespace(damage_reported=True, damage_fee=123.45)
        rendered = tpl.render(Context({'booking': booking}))
        self.assertIn('Damage Reported - Fee: ₹123.45', rendered)

    def test_damage_indicator_shows_no_damage_when_not_reported(self):
        tpl = Template(
            '{% if booking.damage_reported %}Damage Reported - Fee: ₹{{ booking.damage_fee|floatformat:2 }}{% else %}No Damage{% endif %}'
        )
        booking = SimpleNamespace(damage_reported=False, damage_fee=0)
        rendered = tpl.render(Context({'booking': booking}))
        self.assertIn('No Damage', rendered)

    def test_driver_image_check_uses_fallback_when_missing(self):
        tpl = Template(
            '{% if driver.image %}HAS_IMG:{{ driver.image.url }}{% else %}NO_IMG{% endif %}'
        )
        # case: no image
        driver_no_img = SimpleNamespace(image=None, name='Alice')
        rendered_no = tpl.render(Context({'driver': driver_no_img}))
        self.assertIn('NO_IMG', rendered_no)

        # case: has image-like object with .url
        img_obj = SimpleNamespace(url='/media/drivers/alice.jpg')
        driver_with_img = SimpleNamespace(image=img_obj, name='Alice')
        rendered_yes = tpl.render(Context({'driver': driver_with_img}))
        self.assertIn('HAS_IMG:/media/drivers/alice.jpg', rendered_yes)
# ...existing code...