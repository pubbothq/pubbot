from django.views.generic import ListView

from pubbot.tasty.models import Link


class BaseGalleryView(ListView):
    queryset = Link.objects.filter(content_type__startswith="image/").order_by('-first_seen')
    context_object_name = 'link_list'


class GalleryGridView(BaseGalleryView):
    template_name = 'tasty/gallery_grid.html'


class GalleryDetailView(BaseGalleryView):
    template_name = 'tasty/gallery_detail.html'
    paginate_by = 1
