# Copyright (C) <2018> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from django.contrib import admin
from django.urls import include, path

from gcc import staff_views, views

app_name = 'gcc'


PRESENTATION_PATTERNS = [
    path('', views.presentation.IndexView.as_view(), name='index'),
    path('privacy/', views.presentation.PrivacyView.as_view(), name='privacy'),
    path(
        'learn/', views.presentation.LearnMoreView.as_view(), name='learn_more'
    ),
    path(
        'resources/',
        views.presentation.RessourcesView.as_view(),
        name='resources',
    ),
    path(
        'editions/', views.presentation.EditionsView.as_view(), name='editions'
    ),
    path(
        'editions/<int:year>/',
        views.presentation.EditionsView.as_view(),
        name='editions',
    ),
]

NEWSLETTER_PATTERNS = [
    path(
        'unsubscribe/<str:email>/<str:token>/',
        views.newsletter.UnsubscribeView.as_view(),
        name='news_unsubscribe',
    )
]

APPLICATION_PATTERNS = [
    path(
        'validation/<int:pk>/<int:edition>/',
        views.application.ValidationView.as_view(),
        name='application_validation',
    ),
    path(
        'form/<int:edition>/',
        views.application.FormView.as_view(),
        name='application_form',
    ),
    path(
        'wishes/<int:edition>/',
        views.application.WishesView.as_view(),
        name='application_wishes',
    ),
    path(
        'summary/<int:pk>/',
        views.application.SummaryView.as_view(),
        name='application_summary',
    ),
    path(
        'confirm/<int:wish>/',
        views.application.ConfirmVenueView.as_view(),
        name='confirm',
    ),
    # Reviewing
    path(
        'review/',
        staff_views.ApplicationReviewIndexView.as_view(),
        name='application_review_index',
    ),
    path(
        'review/<int:edition>/<int:event>/',
        staff_views.ApplicationReviewView.as_view(),
        name='application_review',
    ),
    path(
        'label_remove/<int:event>/<int:applicant>/<int:label>/',
        staff_views.ApplicationRemoveLabelView.as_view(),
        name='delete_applicant_label',
    ),
    path(
        'label_add/<int:event>/<int:applicant>/<int:label>/',
        staff_views.ApplicationAddLabelView.as_view(),
        name='add_applicant_label',
    ),
    path(
        'update_wish/<int:wish>/<int:status>/',
        staff_views.UpdateWish.as_view(),
        name='update_wish',
    ),
    path(
        'accept_all/<int:event>/',
        staff_views.ApplicationAcceptView.as_view(),
        name='accept_all',
    ),
    path(
        'accept_all_send/<int:event>/',
        staff_views.ApplicationAcceptSendView.as_view(),
        name='accept_all_send',
    ),
]


urlpatterns = [
    path('', include(PRESENTATION_PATTERNS)),
    path('application/', include(APPLICATION_PATTERNS)),
    path('newsletter/', include(NEWSLETTER_PATTERNS)),
    path('admin/', admin.site.urls),
]
