import logging
import structlog
from fastapi import FastAPI, HTTPException, Request
from prometheus_fastapi_instrumentator import Instrumentator

# Configure standard Python logging to output JSON via structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Silence uvicorn's default access logger so it doesn't print plain text
logging.getLogger("uvicorn.access").handlers = []

# Initialize FastAPI application ONCE
app = FastAPI(
    title="Production Reliability Platform",
    description="A hands-on SRE learning project",
    version="0.1.0",
)

# Initialize Prometheus Instrumentator
instrumentator = Instrumentator()

@app.on_event("startup")
async def startup():
    instrumentator.expose(app)
    logger.info("application_startup", status="started", port=8000)

instrumentator.instrument(app)

orders = {
    1: {"id": 1, "item": "Laptop", "status": "shipped"},
    2: {"id": 2, "item": "Keyboard", "status": "processing"},
    3: {"id": 3, "item": "Monitor", "status": "delivered"},
}

@app.get("/")
def root(request: Request):
    logger.info("root_endpoint_invoked", client_ip=request.client.host)
    return {"message": "Production Reliability Platform is running"}

@app.get("/health")
def health(request: Request):
    logger.info("health_check_invoked", client_ip=request.client.host)
    return {"status": "healthy"}

@app.get("/ready")
def readiness(request: Request):
    logger.info("readiness_check_invoked", client_ip=request.client.host)
    return {"status": "ready"}

@app.get("/api/orders")
def get_orders(request: Request):
    logger.info("get_orders_invoked", client_ip=request.client.host, order_count=len(orders))
    return {"orders": list(orders.values())}

@app.get("/api/orders/{order_id}")
def get_order(order_id: int, request: Request):
    logger.info("get_single_order_invoked", client_ip=request.client.host, order_id=order_id)
    if order_id not in orders:
        logger.warning("order_not_found", order_id=order_id)
        raise HTTPException(status_code=404, detail="Order not found")
    return orders[order_id]
