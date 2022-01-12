from django.db.models import Sum
from django.http import HttpResponse

from .models import IngredientForRecipe


def get_send_file(request, filename):
    user = request.user
    ingredients = IngredientForRecipe.objects.filter(
        recipe__purchase__user=user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(
        ingreient_total=Sum('amount')
    )
    text = 'СПИСОК ПОКУПОК:\n'
    for number, ingredient in enumerate(ingredients, start=1):
        text += (f'{number}) '
                 f'{ingredient["ingredient__name"]}: '
                 f'{ingredient["ingreient_total"]} '
                 f'{ingredient["ingredient__measurement_unit"]}\n')
    response = HttpResponse(text, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
