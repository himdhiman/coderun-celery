import cloudinary.uploader

def delete_coudinary_test_cases():
    cloudinary.uploader.destroy()

def delete_cloudinary_image(public_id, resource_type):
    cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    return