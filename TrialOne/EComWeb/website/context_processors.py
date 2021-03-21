from .models import Category

def menu_categories(request):
    menu_categories = Category.objects.all()

    return {'menu_categories':menu_categories}
