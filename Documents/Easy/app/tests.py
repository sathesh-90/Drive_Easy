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
        driver_no_img = SimpleNamespace(image=None, name='Alice')
        rendered_no = tpl.render(Context({'driver': driver_no_img}))
        self.assertIn('NO_IMG', rendered_no)

        img_obj = SimpleNamespace(url='/media/drivers/alice.jpg')
        driver_with_img = SimpleNamespace(image=img_obj, name='Alice')
        rendered_yes = tpl.render(Context({'driver': driver_with_img}))
        self.assertIn('HAS_IMG:/media/drivers/alice.jpg', rendered_yes)

    def test_booking_image_and_damage_details_rendering(self):
        tpl = Template("""
        {% if booking.car and booking.car.image %}
          IMG:{{ booking.car.image.url }}
        {% else %}
          IMG:FALLBACK
        {% endif %}

        <div class="damage-indicator {% if booking.damage_reported %}damage-true{% else %}damage-false{% endif %}">
          {% if booking.damage_reported %}
            Damage Reported - Fee: ₹{{ booking.damage_fee|floatformat:2 }}
            {% if booking.damage_notes %}Notes: {{ booking.damage_notes }}{% endif %}
          {% else %}
            No Damage
          {% endif %}
        </div>

        <div id="damage-details-{{ booking.id }}">
          Fee:₹{{ booking.damage_fee|default:0|floatformat:2 }}
          Notes:{{ booking.damage_notes|default:"" }}
        </div>
        """)
        # case: has car image and damage reported with notes
        img_obj = SimpleNamespace(url='/media/cars/car1.jpg')
        car = SimpleNamespace(image=img_obj, category='Sedan')
        booking1 = SimpleNamespace(
            id=11, car=car, damage_reported=True, damage_fee=250.0, damage_notes='Broken bumper'
        )
        rendered1 = tpl.render(Context({'booking': booking1}))
        self.assertIn('IMG:/media/cars/car1.jpg', rendered1)
        self.assertIn('Damage Reported - Fee: ₹250.00', rendered1)
        self.assertIn('Notes: Broken bumper', rendered1)
        self.assertIn('damage-details-11', rendered1)

        # case: no car image and no damage
        car2 = SimpleNamespace(image=None, category='Hatchback')
        booking2 = SimpleNamespace(id=12, car=car2, damage_reported=False, damage_fee=0, damage_notes='')
        rendered2 = tpl.render(Context({'booking': booking2}))
        self.assertIn('IMG:FALLBACK', rendered2)
        self.assertIn('No Damage', rendered2)
        self.assertIn('damage-details-12', rendered2)