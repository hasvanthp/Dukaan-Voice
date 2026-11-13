# API Endpoints

- `GET /health`
- `POST /api/v1/conversation/voice-command`
- `GET /api/v1/inventory/`
- `POST /api/v1/inventory/add` (confirmation required)
- `POST /api/v1/sales/` (confirmation required)
- `GET /api/v1/sales/report?days=1`
- `POST /api/v1/credits/customers`
- `POST /api/v1/credits/payments` (confirmation required)
- `GET /api/v1/credits/customers/{customer_id}`

All business endpoints require `x-user-id` and `x-store-id` headers.
