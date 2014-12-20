from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
try:
    from django.utils.module_loading import import_string  # Django >= 1.7
except ImportError:
    try:
        from django.utils.module_loading import import_by_path as import_string  # Django == 1.6
    except ImportError:
        # Django <= 1.5
        import sys
        from django.utils import six

        def import_string(dotted_path):
            """
            Import a dotted module path and return the attribute/class designated by the
            last name in the path. Raise ImportError if the import failed.
            """
            try:
                module_path, class_name = dotted_path.rsplit('.', 1)
            except ValueError:
                msg = "%s doesn't look like a module path" % dotted_path
                six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

            module = import_module(module_path)

            try:
                return getattr(module, class_name)
            except AttributeError:
                msg = 'Module "%s" does not define a "%s" attribute/class' % (
                    dotted_path, class_name)
                six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

DEFAULT_COMMENTS_APP = 'django_comments'
DEFAULT_COMMENTS_MODEL = getattr(settings, 'COMMENTS_MODEL', 'django_comments.models.LegacyComment')
DEFAULT_COMMENTS_FORM = getattr(settings, 'COMMENTS_FORM', 'django_comments.forms.LegacyCommentForm')

def get_comment_app():
    """
    Get the comment app (i.e. "django_comments") as defined in the settings
    """
    # Make sure the app's in INSTALLED_APPS
    comments_app = get_comment_app_name()
    if comments_app not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured("The COMMENTS_APP (%r) "\
                                   "must be in INSTALLED_APPS" % settings.COMMENTS_APP)

    # Try to import the package
    try:
        package = import_module(comments_app)
    except ImportError as e:
        raise ImproperlyConfigured("The COMMENTS_APP setting refers to "\
                                   "a non-existing package. (%s)" % e)

    return package

def get_comment_app_name():
    """
    Returns the name of the comment app (either the setting value, if it
    exists, or the default).
    """
    return getattr(settings, 'COMMENTS_APP', DEFAULT_COMMENTS_APP)

def get_model():
    """
    Returns the comment model class.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_model"):
        return get_comment_app().get_model()
    else:
        comment_model = import_string(DEFAULT_COMMENTS_MODEL)
        comment_model._meta.managed = True
        return comment_model

def get_form():
    """
    Returns the comment ModelForm class.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_form"):
        return get_comment_app().get_form()
    else:
        return import_string(DEFAULT_COMMENTS_FORM)

def get_form_target():
    """
    Returns the target URL for the comment form submission view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_form_target"):
        return get_comment_app().get_form_target()
    else:
        return urlresolvers.reverse("django_comments.views.comments.post_comment")

def get_flag_url(comment):
    """
    Get the URL for the "flag this comment" view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_flag_url"):
        return get_comment_app().get_flag_url(comment)
    else:
        return urlresolvers.reverse("django_comments.views.moderation.flag",
                                    args=(comment.id,))

def get_delete_url(comment):
    """
    Get the URL for the "delete this comment" view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_delete_url"):
        return get_comment_app().get_delete_url(comment)
    else:
        return urlresolvers.reverse("django_comments.views.moderation.delete",
                                    args=(comment.id,))

def get_approve_url(comment):
    """
    Get the URL for the "approve this comment from moderation" view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_approve_url"):
        return get_comment_app().get_approve_url(comment)
    else:
        return urlresolvers.reverse("django_comments.views.moderation.approve",
                                    args=(comment.id,))
