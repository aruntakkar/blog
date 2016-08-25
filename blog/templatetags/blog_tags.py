from django import template
from django.db.models import Count
from ..models import Post

from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.assignment_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

"""
	Finally we're going to create an assignment tags are simple
	tags but they store the results in given variable.
"""


"""
	Django Provides the following helper functions that
	allow you to create your own template tags in an
	easy manner.

	simple_tag: Process the data and returns a string.

	inclusion_tag: Process the data and returns a rendered template.

	(using an inclusion tag, you can render a template with context variables
	returned by your template tag.)

	(inclusion tags have to return a dictionary of values that is used as the
	context to render the specified template, inclusion tags returns a dictionary.)

	(template tag we just created can be used passing the optional number of comments
	to display like)

	assignment_tag: Process the data and sets a variable in the context.
"""
