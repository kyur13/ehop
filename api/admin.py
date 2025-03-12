
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,product,Cart,categories,price_range,Order,blog

class customeuseradmin(UserAdmin):
    model=CustomUser

    list_display=['id','email','first_name','last_name','age','gender','is_staff','is_active']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Define the fields to display in the "Add user" page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'is_staff'),
        }),
    )
    search_fields=('email',)
    ordering=('email',)
admin.site.register(CustomUser, customeuseradmin)

@admin.register(product)
class productadmin(admin.ModelAdmin):
    list_display=['id','name','category','price','img']

# @admin.register(Cart)
# class cartadmin(admin.ModelAdmin):
#     list_display=['id','user']

@admin.register(Cart)
class cartitemadmin(admin.ModelAdmin):
    list_display=['id','user','cart_product','quantity']

    search_fields=['user__email']

@admin.register(categories)
class categoryadmin(admin.ModelAdmin):
    list_display=['id','name']

@admin.register(price_range)
class price_rangeadmin(admin.ModelAdmin):
    list_display=['id','range']


def cancel_order_action(modeladmin, request, queryset):
    for order in queryset:
        order.cancle_order()  # Call the cancel_order method to change status and send email
    modeladmin.message_user(request, "Selected orders have been cancelled.")

import openpyxl
from django.http import HttpResponse
def export_to_excel(modeladmin, request, queryset):
    # Create a new workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Orders"

    # Define the headers
    headers = [
        'Order ID', 'Image', 'Product', 'User', 'Quantity', 'Price', 'Total', 'Address', 'Phone', 'Pincode', 'Status'
    ]
    ws.append(headers)

    # Add data from queryset to the Excel sheet
    for order in queryset:
        row = [
            order.id,
            order.image.url if order.image else '',
            order.ord_product if order.ord_product else '',
            order.user.email if order.user else '',
            order.quantity,
            order.price,
            order.total,
            order.address,
            order.phone,
            order.pincod,
            order.status,
        ]
        ws.append(row)

    # Create the HttpResponse object with the correct content type for an Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=orders.xlsx'
    wb.save(response)
    return response

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
def export_to_pdf(modeladmin, request, queryset):
    # Create a response object with content-type 'application/pdf'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=orders.pdf'

    # Create a SimpleDocTemplate for PDF generation
    pdf = SimpleDocTemplate(response, pagesize=letter)
    
    # Create a list to hold the data in a table format
    data = []

    # Define the table headers
    headers = [
        'Order ID', 'Product', 'User', 'Quantity', 'Price', 'Total', 'Address', 'Phone', 'Pincode', 'Status'
    ]
    data.append(headers)

    # Add data from queryset to the table
    for order in queryset:
        row = [
            order.id,
            order.ord_product if order.ord_product else 'N/A',
            order.user.email if order.user else 'N/A',
            order.quantity,
            order.price,
            order.total,
            order.address,
            order.phone,
            order.pincod,
            order.status,
        ]
        data.append(row)

    # Create the Table object and apply table style
    table = Table(data)

    # Define table style (for borders, font size, alignment, etc.)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center all text
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold headers
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Gridlines for all cells
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Regular font for data rows
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Font size for the entire table
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for headers
        ('TOPPADDING', (0, 0), (-1, 0), 12),  # Padding for headers
    ])

    # Apply the style to the table
    table.setStyle(style)

    # Build the PDF document with the table
    elements = [table]
    pdf.build(elements)

    return response

@admin.register(Order)
class Orderadmin(admin.ModelAdmin):
    list_display=['id','image','ord_product','user','quantity','price','total','address','phone','pincod','status']
    actions = [cancel_order_action,export_to_excel,export_to_pdf]
    search_fields=('ord_product','status')

@admin.register(blog)
class blogadmin(admin.ModelAdmin):
    list_display=['name','body']