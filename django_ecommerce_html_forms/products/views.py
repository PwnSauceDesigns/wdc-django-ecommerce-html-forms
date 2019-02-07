from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

from products.models import Product, Category, ProductImage


def products(request):
    products = Product.objects.all()
    # Get up to 4 `featured=true` Products to be displayed on top
    featured_products = products.filter(featured=True)[:4]
    return render(request, 'products.html', {'products': products, 'featured_products': featured_products})


def create_product(request):
    # Get all categories from the DB
    categories = Category.objects.all()

    if request.method == 'POST':
        fields = ['name', 'sku', 'price']
        errors = {}

        for field in fields:
            if request.POST.get(field):
                pass
            else:
                errors[field] = 'You must fill this out'

        if errors:
            return render(request, 'create_product.html', {'errors': errors, 'categories': categories, 'payload': request.POST})

        # name validation: can't be longer that 100 characters
        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name can't be longer than 100 characters."

        # SKU validation: it must contain 8 alphanumeric characters
        SKU = request.POST.get('sku')
        if len(SKU) != 8:
            errors['sku'] = 'Sku must be 8 characters long. Numbers and letters only.'

        # Price validation: positive float lower than 10000.00
        price = request.POST.get('price')
        if float(price) < 0 or float(price) > 9999.99:
            errors['price'] = "Price can't be negative, and must be under 9999.99"

        # if any errors so far, render 'create_product.html' sending errors and
        if errors:
            return render(request, 'create_product.html', {'categories': categories, 'errors': errors, 'payload': request.POST})

        category = Category.objects.get(name=request.POST.get('category'))
        product = Product.objects.create(name=request.POST['name'],
                                        sku=request.POST['sku'],
                                        price=float(request.POST.get('price')),
                                        category=category,
                                        description=request.POST.get('description', None)
                                        )

        images = []
        for num in range(1, 4):
            picture = request.POST.get('image_{}'.format(num))
            if picture:
                images.append(picture)

        for image_url in images:
            ProductImage.objects.create(product=product, url=image_url)

        return redirect('products')

    return render(request, 'create_product.html', {'categories': categories})


def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        fields = ['name', 'sku', 'price']
        errors = {}
        for field in fields:
            if not request.POST.get(field):
                errors[field] = 'This field is required.'

        if errors:
            return render(request, 'edit_product.html', {'product': product, 'categories': categories, 'errors': errors, 'payload': request.POST})

        # check name
        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name cannot be longer than 100 characters."

        # check sku
        sku = request.POST.get('sku')
        if len(sku) != 8:
            errors['sku'] = "SKU be made of 8 alphanumeric characters."

        # check price
        price = request.POST.get('price')
        if float(price) < 0 or float(price) > 9999.99 :
            errors['price'] = "Price can't be negative, and must be under 9999.99"

        if errors:
            return render(request, 'edit_product.html', {'product': product, 'categories': categories, 'errors': errors, 'payload': request.POST})

        product.name = request.POST.get('name')
        product.sku = request.POST.get('sku')
        product.price = float(request.POST.get('price'))
        product.description = request.POST.get('description')

        category = Category.objects.get(name=request.POST.get('category'))

        product.category = category
        product.save()

        new_images = []
        for i in range(1, 4):
            new_image = request.POST.get('image_{}'.format(i))
            if new_image:
                new_images.append(new_image)

        old_images = [image.url for image in product.productimage_set.all()]

        # delete images that didn't come in request.POST
        images_to_delete = []
        for image in old_images:
            if image not in new_images:
                images_to_delete.append(image)

        ProductImage.objects.filter(url__in=images_to_delete).delete()  # bulk delete

        # create images that came in request.POST
        for image in new_images:
            if image not in old_images:
                ProductImage.objects.create(product=product, url=image)

        return redirect('products')
    return render(request, 'edit_product.html', {'product': product, 'categories': categories, 'images': [image.url for image in product.productimage_set.all()]})


def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == "POST":
        product.delete()
        return redirect('products')
    return render(request, 'delete_product.html', {'product': product})


def toggle_featured(request, product_id):
    product = Product.objects.get(id=product_id)
    product.featured = not product.featured
    product.save()
    return redirect('products')
