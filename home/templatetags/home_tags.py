from django import template

from home.models import NavigationMenu

register = template.Library()


# Navigation menus
@register.assignment_tag(takes_context=False)
def get_navigation_menu(menu_name):
    menu = NavigationMenu.objects.filter(menu_name=menu_name)

    if menu:
        return menu[0].menu_items.all()
    else:
        return None