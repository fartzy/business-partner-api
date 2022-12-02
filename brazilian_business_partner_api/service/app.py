import fastapi

from brazilian_business_partner_api.service.controller import company

app = fastapi.FastAPI()
app.include_router(company.company_router)
