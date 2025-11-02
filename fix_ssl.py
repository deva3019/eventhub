import certifi
import ssl

# Print the path to certifi's certificates
print(f"Certifi path: {certifi.where()}")

# Create SSL context with proper certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())
print("SSL context created successfully")
