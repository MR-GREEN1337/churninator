# backend/src/api/v1/endpoints/billing.py
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.src.core.settings import get_settings
from backend.src.db.postgresql import get_session
from backend.src.db.models.user import User
from backend.src.api.v1.dependencies import get_current_user

router = APIRouter()
settings = get_settings()
stripe.api_key = settings.STRIPE_API_KEY


@router.post("/create-checkout-session")
async def create_checkout_session(
    price_id: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    customer_id = current_user.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            email=current_user.email, name=current_user.full_name
        )
        customer_id = customer.id
        current_user.stripe_customer_id = customer_id
        db.add(current_user)
        await db.commit()

    try:
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.CLIENT_URL}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.CLIENT_URL}/billing",
        )
        return {"sessionId": checkout_session.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create-portal-session")
async def create_portal_session(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="User is not a Stripe customer.")

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=f"{settings.CLIENT_URL}/billing",
        )
        return {"url": portal_session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_session)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")

        # Update user with subscription details
        user = await db.get(User, {"stripe_customer_id": customer_id})
        if user:
            user.subscription_id = subscription_id
            subscription = stripe.Subscription.retrieve(subscription_id)
            user.subscription_status = subscription.status
            user.plan_id = subscription.items.data[0].price.id
            db.add(user)
            await db.commit()

    # Add more event handlers here (e.g., invoice.payment_succeeded, customer.subscription.deleted)

    return {"status": "success"}
