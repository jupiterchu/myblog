import json

import markdown
from django.core.cache import cache
from django.core.serializers import serialize, deserialize
from django.views.generic import TemplateView

from myblog.models import *


def get_left_value(categories=None, tags=None):

    if not categories:
        categories = Category.objects.all()
    tmp_dict = {}
    for category in categories:
        name = category.name
        tmp_dict.setdefault(name, {'name': name, 'url': None, 'count': 0})
        tmp_dict[name]['url'] = category.permalink
        tmp_dict[name]['count'] += 1

    categories = tmp_dict.values()

    if not tags:
        tags = Tag.objects.all()
    tmp_dict = {}
    for tag in tags:
        name = tag.name
        tmp_dict.setdefault(name, {'name': name, 'url': None, 'count': 0})
        tmp_dict[name]['url'] = tag.permalink
        tmp_dict[name]['count'] += 1

    tags = tmp_dict.values()

    return tags, categories

class IndexView(TemplateView):
    template_name = 'new_index.html'

    def get(self, request, *args, **kwargs):
        articles = Article.objects.order_by('create_time')
        for article in articles:
            article.length = len(article.context)
            article.read_time = article.length // 180 if article.length // 180 else 1
            article.categories = article.category_set.values()
            article.tags = article.tag_set.values()

        l_tags, l_categories = get_left_value()
        return self.render_to_response(context=locals())


class DetailView(TemplateView):
    template_name = 'new_detail.html'

    def get(self, request, *args, **kwargs):
        article = Article.objects.get(url=request.path)
        categories = article.category_set.values()[0]
        tags = article.tag_set.values()[0]
        article.length = len(article.context)
        article.read_time = article.length // 180 if article.length // 180 else 1
        article.context = markdown.markdown(article.context,
                                            extensions=['extra', 'codehilite', 'toc', ],
                                            safe_mode=True,
                                            enable_attributes=False
                                            )
        try:
            next_article = Article.objects.raw(
                f"select * from {Article._meta.db_table} where id > {article.id} order by id desc limit 1")
            next_article = next_article[0]
        except Exception as e:
            print("could not find next article")

        l_tags, l_categories = get_left_value()
        current_path=request.get_raw_uri()
        return self.render_to_response(locals())


class ArchiveView(TemplateView):
    template_name = 'archives.html'

    def get(self, request, *args, **kwargs):

        cache_value = cache.get('archives_cache')

        if cache_value:
            archives = []
            serialized_archives = json.loads(cache_value)
            count = 0
            for archive in serialized_archives:
                archives.append({
                    'articles': [item.object for item in deserialize('json', archive['articles'])],
                    'year': archive['year']
                })
                count += len(json.loads(archive['articles']))

        else:
            articles = Article.objects.all()
            tmp_dict = {}

            for article in articles:
                year = article.create_time.strftime('%Y')
                tmp_dict.setdefault(year, {'year': year, 'articles': []})
                tmp_dict[year]['articles'].append(article)

            archives = tmp_dict.values()
            count = len(articles)

            serialized_archives = []
            for archive in list(archives):
                serialized_archives.append({
                    'year': archive['year'],
                    'articles': serialize('json', archive['articles'])
                })
            cache.set('archives_cache', json.dumps(serialized_archives))
            cache.expire('archives_cache', 30)

        l_tags, l_categories = get_left_value()
        return self.render_to_response(locals())


class CategoryView(TemplateView):
    template_name = 'categories.html'

    def get(self, request, *args, **kwargs):
        name = kwargs.get('name')
        tmp_dict = {}

        if not name:
            categories = Category.objects.all()
        else:
            categories = Category.objects.filter(name=name)
        for category in categories:
            name = category.name
            tmp_dict.setdefault(name, {'name': name, 'url': None, 'articles': [], 'count': 0})
            tmp_dict[name]['articles'].append(category.article)
            tmp_dict[name]['url'] = category.permalink
            tmp_dict[name]['count'] += 1


        l_tags, l_categories = get_left_value()

        categories = tmp_dict.values()
        length_categories = len(categories)

        return self.render_to_response(locals())


class TagView(TemplateView):
    template_name = 'tags.html'

    def get(self, request, *args, **kwargs):
        name = kwargs.get('name')
        if not name:
            tags = Tag.objects.all()

        else:
            tags = Tag.objects.filter(name=name)

        l_tags, l_categories = get_left_value()

        tmp_dict = {}
        for tag in tags:
            name = tag.name
            tmp_dict.setdefault(name, {'name': name, 'url': None, 'articles': [], 'count': 0})
            tmp_dict[name]['articles'].append(tag.article)
            tmp_dict[name]['url'] = tag.permalink
            tmp_dict[name]['count'] += 1

        tags = tmp_dict.values()


        return self.render_to_response(locals())

