from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count
from taggit.models import Tag
from haystack.query import SearchQuerySet
from .forms import EmailPostForm, CommentForm, SearchForm
from .models import Post, Comment

def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)  # 3 posts in each Page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is out of range deliver the last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts':
                                                   posts, 'tag': tag})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year, publish__month=month, publish__day=day)

    # list of active comments for this post
    comments = post.comments.filter(active=True)

    if request.method == 'POST':
        # A method was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # create comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the Current post to the Comment
            new_comment.post = post
            # save the comment to the Database
            new_comment.save()
    else:
        comment_form = CommentForm()
    # list of Similar Posts
    # We retrive a Python list of ID's for the tags of the current post
    # The value_list() QuerySet returns tuples with the values for the given fields,
    # We are passing it flat=True to get a flat list like [1,2,3,....]
    post_tags_ids = post.tags.values_list('id', flat=True)

    # We get all the posts that contain any of these tags excluding the
    # current post itself.
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
        .exclude(id=post.id)

    # We Use the Count aggregation function to generate a calculated field same_tags
    # that contains the number of tags shared with all the tags queried.

    # We order the result by the number of shared tags(descendant order) and
    # publish to display recent posts first for the posts with the same number
    # of shared tags, we slice the results to retreive only the fist four
    # posts.

    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
        .order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'comment_form': comment_form, 'similar_posts': similar_posts})


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    cd = {}

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
                # Form fields passed Validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading: "{}"'.format(
                cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'. format(
                post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'your_email@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent, 'cd': cd})

def post_search(request):
    results = 0
    total_results = 0
    form = SearchForm()
    cd = {}
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            results = SearchQuerySet().models(Post).filter(content=cd['query']).load_all()
            # count total_results
            total_results = results.count()
    return render(request, 'blog/post/search.html', {'form': form, 'cd': cd, 'results': results, 'total_results': total_results})