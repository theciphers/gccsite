from django.contrib import admin
from django.urls import include, path
from gcc import views, staff_views


app_name = 'gcc'

NEWSLETTER_PATTERNS = [
    path(
        'unsubscribe/<str:email>/<str:token>/',
        views.NewsletterUnsubscribeView.as_view(),
        name='news_unsubscribe'),
]

APPLICATION_PATTERNS = [
    path('review/',
         staff_views.ApplicationReviewIndexView.as_view(),
         name='application_review_index'),
    path('review/<int:edition>/<int:event>/',
         staff_views.ApplicationReviewView.as_view(),
         name='application_review'),
    path('validation/<int:pk>/<int:edition>/',
         views.ApplicationValidationView.as_view(),
         name='application_validation'),
    path('form/<int:edition>/',
         views.ApplicationFormView.as_view(),
         name='application_form'),
    path('wishes/<int:edition>/',
         views.ApplicationWishesView.as_view(),
         name='application_wishes'),
    path('summary/<int:pk>/',
         views.ApplicationSummaryView.as_view(),
         name='application_summary'),
    path('label_remove/<int:event>/<int:applicant>/<int:label>/',
         staff_views.ApplicationRemoveLabelView.as_view(),
         name='delete_applicant_label'),
    path('label_add/<int:event>/<int:applicant>/<int:label>/',
         staff_views.ApplicationAddLabelView.as_view(),
         name='add_applicant_label'),
    path('update_wish/<int:wish>/<int:status>/',
         staff_views.UpdateWish.as_view(),
         name='update_wish')
]

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('application/', include(APPLICATION_PATTERNS)),
    path('newsletter/', include(NEWSLETTER_PATTERNS)),
    path('learn/', views.LearnMoreView.as_view(), name='learn_more'),
    path('resources/', views.RessourcesView.as_view(), name='resources'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),

    path('editions/', views.EditionsView.as_view(), name='editions'),
    path('editions/<int:year>/', views.EditionsView.as_view(),
         name='editions'),

    # Admin panel
    path('admin/', admin.site.urls),
]
