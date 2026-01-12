from celery import shared_task
from django.db import models
from .models import ProductRating, Review, Product


@shared_task
def update_product_rating(product_id):
    """
    Background task to update product rating and total reviews count.
    This runs asynchronously after a review is created, updated, or deleted.
    """
    try:
        product = Product.objects.get(id=product_id)
        reviews = product.reviews.all()
        total_reviews = reviews.count()
        
        # Calculate average rating
        review_average = reviews.aggregate(
            models.Avg("rating")
        )["rating__avg"] or 0.0
        
        # Get or create ProductRating instance
        product_rating, created = ProductRating.objects.get_or_create(
            product=product
        )
        
        # Update the rating
        product_rating.average_rating = review_average
        product_rating.total_reviews = total_reviews
        product_rating.save()
        
        return f"Updated rating for {product.name}: {review_average:.2f} stars ({total_reviews} reviews)"
    
    except Product.DoesNotExist:
        return f"Error: Product with id {product_id} not found"
    
    except Exception as e:
        return f"Error updating product rating: {str(e)}"


@shared_task
def test_celery_task():
    """
    Simple test task to verify Celery is working correctly.
    Run this to test: test_celery_task.delay()
    """
    return "Celery is working successfully! 🚀"


@shared_task
def bulk_update_all_product_ratings():
    """
    Background task to recalculate ratings for ALL products.
    Useful for maintenance or after data imports.
    Run manually when needed.
    """
    try:
        products = Product.objects.all()
        updated_count = 0
        
        for product in products:
            reviews = product.reviews.all()
            total_reviews = reviews.count()
            
            review_average = reviews.aggregate(
                models.Avg("rating")
            )["rating__avg"] or 0.0
            
            product_rating, created = ProductRating.objects.get_or_create(
                product=product
            )
            
            product_rating.average_rating = review_average
            product_rating.total_reviews = total_reviews
            product_rating.save()
            
            updated_count += 1
        
        return f"Successfully updated ratings for {updated_count} products"
    
    except Exception as e:
        return f"Error in bulk update: {str(e)}"


@shared_task(bind=True, max_retries=3)
def retry_example_task(self, product_id):
    """
    Example task with retry logic.
    If it fails, it will retry up to 3 times with exponential backoff.
    """
    try:
        product = Product.objects.get(id=product_id)
        # Do something with the product
        return f"Task completed for {product.name}"
    
    except Product.DoesNotExist:
        return f"Product {product_id} not found"
    
    except Exception as exc:
        # Retry after 60 seconds, then 120, then 240 (exponential backoff)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

        