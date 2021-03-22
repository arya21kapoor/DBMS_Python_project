from .models import Category

# Used for the menu bar in homePage.html

def menu_categories(request):
    menu_categories = Category.objects.all()
    return {'menu_categories':menu_categories}
