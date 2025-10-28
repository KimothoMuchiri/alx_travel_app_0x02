# alx_travel_app_0x02 
## Overview
This task focuses on integrating the Chapa Payment Gateway into a Django-based travel booking application. Learners will implement secure payment initiation, verification, and status handling for bookings. The workflow covers creating models for payment tracking, API endpoints for initiating and verifying payments, and integrating background email notifications upon successful payment.

## Learning Objectives
By the end of this task, learners will be able to:

    - Configure and securely store API credentials for third-party payment gateways.
    - Create Django models to manage and track payment transactions.
    - Build API endpoints for payment initiation and verification.
    - Implement payment workflows integrated into a booking system.
    - Handle payment status updates and transaction logging.
    - Test payment flows using a sandbox environment.
## Learning Outcomes
Upon completing this task, learners will be able to:

    - Successfully connect a Django application to the Chapa API.
    - Initiate payments and direct users to secure payment pages.
    - Verify payment statuses and update records accordingly.
    - Send automated confirmation emails after successful transactions.
    - Demonstrate a fully functional and tested payment flow in a booking context.  

## Key Concepts
- API Integration – Connecting Django with the Chapa API for payment processing.
- Secure Credential Management – Storing API keys in environment variables.
- Django Models – Structuring and persisting payment transaction data.
- HTTP Requests – Sending POST and GET requests to initiate and verify payments.
- Asynchronous Tasks – Using Celery for sending confirmation emails.
- Error Handling – Managing failed or incomplete payments gracefully.

## Tools and Libraries
- Django – Backend framework for building the application.
- PostgreSQL – Database for persisting bookings and payment data.
- Chapa API – Payment gateway for initiating and verifying transactions.
- Requests – Python library for making API calls to Chapa.
- Celery – For background email sending after successful payment.
- dotenv – For managing environment variables securely.