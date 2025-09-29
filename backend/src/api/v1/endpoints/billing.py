# backend/src/api/v1/endpoints/billing.py
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from datetime import datetime

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
            # --- START: Updated URLs ---
            success_url=f"{settings.CLIENT_URL}/dashboard/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.CLIENT_URL}/dashboard/payment/cancel",
            # --- END: Updated URLs ---
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
            return_url=f"{settings.CLIENT_URL}/settings/billing",  # Return to the billing page after portal session
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
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")

        # Find user by stripe_customer_id
        result = await db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.subscription_id = subscription_id
            subscription = stripe.Subscription.retrieve(subscription_id)
            user.subscription_status = subscription.status
            user.plan_id = subscription.items.data[0].price.id
            db.add(user)
            await db.commit()

    # Handle subscription updates and cancellations
    if event["type"] in [
        "customer.subscription.updated",
        "customer.subscription.deleted",
    ]:
        subscription = event["data"]["object"]
        subscription_id = subscription.id

        """result = await db.execute(
            select(User).where(User.subscription_id == subscription_id)
        )
        user: User = result.scalar_one_or_none()"""

        if user:
            user.subscription_status = subscription.status
            # If the subscription is deleted, we can nullify some fields
            if subscription.status == "canceled":
                user.subscription_ends_at = (
                    datetime.fromtimestamp(subscription.cancel_at)
                    if subscription.cancel_at
                    else None
                )
            db.add(user)
            await db.commit()

    return {"status": "success"}
