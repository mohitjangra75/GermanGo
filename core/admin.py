from django.contrib import admin

# The admin holds courses and the enquiry inbox; every other piece of
# content lives in each app's content.py.
admin.site.site_header = "GermanGo — Site Manager"
admin.site.site_title = "GermanGo admin"
admin.site.index_title = "Courses and enquiries"
