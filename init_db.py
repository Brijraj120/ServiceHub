from app import app, db, Service, ServiceProvider
import random

# Sample data
services = [
    {
        'name': 'Plumbing',
        'description': 'Professional plumbing services for residential and commercial properties.'
    },
    {
        'name': 'Electrical',
        'description': 'Certified electricians for all your electrical needs.'
    },
    {
        'name': 'Carpentry',
        'description': 'Expert carpentry services for home repairs and renovations.'
    },
    {
        'name': 'Cleaning',
        'description': 'Professional cleaning services for homes and offices.'
    },
    {
        'name': 'Gardening',
        'description': 'Landscaping and garden maintenance services.'
    },
    {
        'name': 'Automotive',
        'description': 'Car repair and maintenance services.'
    },
    {
        'name': 'Ambulance',
        'description': 'Emergency medical transportation services available 24/7.'
    },
    {
        'name': 'Police',
        'description': 'Law enforcement and emergency response services.'
    },
    {
        'name': 'Fire Fighter',
        'description': 'Emergency fire response and rescue services.'
    }
]

providers = [
    {
        'service_name': 'Plumbing',
        'name': 'John Smith',
        'phone': '555-123-4567',
        'email': 'john.smith@example.com',
        'address': '123 Main St, Anytown, USA',
        'rating': 4.8
    },
    {
        'service_name': 'Electrical',
        'name': 'Sarah Johnson',
        'phone': '555-234-5678',
        'email': 'sarah.johnson@example.com',
        'address': '456 Oak Ave, Anytown, USA',
        'rating': 4.7
    },
    {
        'service_name': 'Carpentry',
        'name': 'Mike Brown',
        'phone': '555-345-6789',
        'email': 'mike.brown@example.com',
        'address': '789 Pine Rd, Anytown, USA',
        'rating': 4.5
    },
    {
        'service_name': 'Cleaning',
        'name': 'Emily Davis',
        'phone': '555-456-7890',
        'email': 'emily.davis@example.com',
        'address': '101 Maple Dr, Anytown, USA',
        'rating': 4.9
    },
    {
        'service_name': 'Gardening',
        'name': 'David Wilson',
        'phone': '555-567-8901',
        'email': 'david.wilson@example.com',
        'address': '202 Elm St, Anytown, USA',
        'rating': 4.6
    },
    {
        'service_name': 'Ambulance',
        'name': 'City Emergency Medical Services',
        'phone': '555-911-1234',
        'email': 'dispatch@cityems.example.com',
        'address': '500 Hospital Way, Anytown, USA',
        'rating': 4.9
    },
    {
        'service_name': 'Police',
        'name': 'Anytown Police Department',
        'phone': '555-911-2345',
        'email': 'dispatch@anytownpd.example.com',
        'address': '600 Justice Ave, Anytown, USA',
        'rating': 4.8
    },
    {
        'service_name': 'Fire Fighter',
        'name': 'Anytown Fire Department',
        'phone': '555-911-3456',
        'email': 'dispatch@anytownfd.example.com',
        'address': '700 Rescue Blvd, Anytown, USA',
        'rating': 4.9
    },
    {
        'service_name': 'Automotive',
        'name': 'Robert Garcia',
        'phone': '555-789-0123',
        'email': 'robert.garcia@example.com',
        'address': '404 Birch Blvd, Anytown, USA',
        'rating': 4.7
    }
]

def init_db():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Add services
        service_objects = {}
        for service_data in services:
            service = Service(name=service_data['name'], description=service_data['description'])
            db.session.add(service)
            service_objects[service_data['name']] = service
        
        db.session.commit()
        
        # Add service providers
        for provider_data in providers:
            service = service_objects[provider_data['service_name']]
            provider = ServiceProvider(
                name=provider_data['name'],
                service_id=service.id,
                phone=provider_data['phone'],
                email=provider_data['email'],
                address=provider_data['address'],
                rating=provider_data['rating']
            )
            db.session.add(provider)
        
        db.session.commit()
        
        print("Database initialized with sample data!")

if __name__ == "__main__":
    init_db() 