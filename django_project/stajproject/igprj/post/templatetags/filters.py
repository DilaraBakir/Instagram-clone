from django import template
register = template.Library()


@register.filter
def get_by_post_id(like_counts, post_id):
    return like_counts.get(post_id, 0)