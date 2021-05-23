from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render

from devpro.encurtador.models import UrlLog, UrlRedirect

# Create your views here.


def relatorios(requisicao, slug):
    url_redirect = UrlRedirect.objects.get(slug=slug)
    url_reduzida = requisicao.build_absolute_uri(f'/{slug}')
    redirec_por_data = list(
        UrlRedirect.objects.filter(
            slug=f'{slug}'
        ).annotate(
            data=TruncDate('logs__criado_em')
        ).annotate(
            cliques=Count('data')
        ).order_by('data')
    )
    contexto = {
        'reduce': url_redirect,
        'url_reduzida': url_reduzida,
        'redirec_por_data':  redirec_por_data,
        'total_cliques': sum(r.cliques for r in redirec_por_data)
    }
    return render(requisicao, 'encurtador/relatorio.html', contexto)


def redirecionar(requisicao, slug):
    url_redirect = UrlRedirect.objects.get(slug=slug)
    UrlLog.objects.create(
        origem = requisicao.META.get('HTTP_REFERER'),
        user_agent = requisicao.META.get('HTTP_USER_AGENT'),
        host = requisicao.META.get('HTTP_HOST'),
        ip = requisicao.META.get('REMOTE_ADDR'),
        url_redirect = url_redirect
    )
    return redirect(url_redirect.destino)
