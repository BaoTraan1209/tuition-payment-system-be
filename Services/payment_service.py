
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from Models.payment import Payment
from Models.payment_log import PaymentLog

from Repositories.payment_repository import PaymentRepository
from Repositories.payment_log_repository import PaymentLogRepository
from Repositories.tuition_fee_repository import TuitionFeeRepository

from VNPAY.Services.vnpay_service import VnpayService

from Enums.payment_status_enum import PaymentStatusEnum
from Enums.payment_event_enum import PaymentEventEnum
from Enums.tuition_fee_status_enum import TuitionFeeStatusEnum


class PaymentService:

    def __init__(self, db: Session):
        self.db = db

        self.payment_repository = PaymentRepository(db)
        self.payment_log_repository = PaymentLogRepository(db)
        self.tuition_fee_repository = TuitionFeeRepository(db)

        self.vnpay_service = VnpayService()

    def create_payment(
        self,
        user_id: str,
        tuition_fee_id: int,
        ip_address: str
    ) -> dict:

        try:
            tuition_fee = self.tuition_fee_repository.find_by_id_for_update(
                tuition_fee_id
            )

            if not tuition_fee or str(tuition_fee.user_id) != str(user_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tuition fee not found"
                )

            if tuition_fee.status == TuitionFeeStatusEnum.PAID.value:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This tuition fee has already been paid"
                )

            if tuition_fee.status != TuitionFeeStatusEnum.UNPAID.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tuition fee is not available for payment"
                )

            pending_payment = self.payment_repository.find_pending_by_tuition_fee_id(
                tuition_fee_id
            )

            if pending_payment:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A payment transaction is already pending"
                )

            amount = tuition_fee.amount
            order_id = uuid.uuid4().hex

            payment = Payment(
                order_id=order_id,
                user_id=user_id,
                tuition_fee_id=tuition_fee.id,
                amount=amount,
                status=PaymentStatusEnum.PENDING.value
            )

            self.payment_repository.save(payment)

            self.payment_log_repository.save(
                PaymentLog(
                    payment_id=payment.id,
                    event=PaymentEventEnum.CREATED.value,
                    message="Payment transaction created"
                )
            )

            payment_url = self.vnpay_service.create_payment_url(
                order_id=order_id,
                amount=amount,
                ip_address=ip_address
            )

            self.db.commit()

            return {
                "payment": payment,
                "payment_url": payment_url
            }

        except HTTPException:
            self.db.rollback()
            raise

        except Exception:
            self.db.rollback()
            raise

    def get_payment_history(self, user_id: str):

        payments = self.payment_repository.find_by_user_id(user_id)

        return [
            {
                "order_id": payment.order_id,
                "amount": payment.amount,
                "status": payment.status,
                "transaction_no": payment.vnp_transaction_no,
                "response_code": payment.response_code,
                "created_at": payment.created_at.isoformat()
            }
            for payment in payments
        ]

    def handle_return(self, params: dict) -> dict:

        if not self.vnpay_service.verify_payment_response(params):
            return {
                "success": False,
                "message": "Invalid payment signature"
            }

        order_id = params.get("vnp_TxnRef")

        if not order_id:
            return {
                "success": False,
                "message": "Missing order ID"
            }

        payment = self.payment_repository.find_by_order_id(order_id)

        if not payment:
            return {
                "success": False,
                "message": "Payment not found"
            }

        amount = params.get("vnp_Amount")

        if not amount or not str(amount).isdigit():
            return {
                "success": False,
                "message": "Invalid payment amount"
            }

        if int(amount) != payment.amount * 100:
            return {
                "success": False,
                "message": "Invalid payment amount"
            }

        return {
            "success": True,
            "order_id": payment.order_id,
            "amount": payment.amount,
            "status": payment.status,
            "response_code": params.get("vnp_ResponseCode"),
            "message": "Payment response received"
        }

    def handle_ipn(self, params: dict) -> dict:

        try:
            if not self.vnpay_service.verify_ipn_response(params):
                return {
                    "RspCode": "97",
                    "Message": "Invalid signature"
                }

            order_id = params.get("vnp_TxnRef")

            if not order_id:
                return {
                    "RspCode": "01",
                    "Message": "Order not found"
                }

            payment = self.payment_repository.find_by_order_id_for_update(
                order_id
            )

            if not payment:
                return {
                    "RspCode": "01",
                    "Message": "Order not found"
                }

            amount = params.get("vnp_Amount")

            if not amount or not str(amount).isdigit():
                return {
                    "RspCode": "04",
                    "Message": "Invalid amount"
                }

            if int(amount) != payment.amount * 100:
                return {
                    "RspCode": "04",
                    "Message": "Invalid amount"
                }

            if payment.status != PaymentStatusEnum.PENDING.value:
                return {
                    "RspCode": "02",
                    "Message": "Order already confirmed"
                }

            response_code = params.get("vnp_ResponseCode")
            transaction_status = params.get("vnp_TransactionStatus")
            transaction_no = params.get("vnp_TransactionNo")

            if response_code == "00" and transaction_status == "00":

                tuition_fee = self.tuition_fee_repository.find_by_id_for_update(
                    payment.tuition_fee_id
                )

                if not tuition_fee:
                    self.db.rollback()
                    return {
                        "RspCode": "01",
                        "Message": "Tuition fee not found"
                    }

                payment.status = PaymentStatusEnum.SUCCESS.value

                if tuition_fee.status == TuitionFeeStatusEnum.PAID.value:
                    message = (
                        "Payment succeeded but tuition fee was already paid. "
                        "Manual refund or reconciliation is required."
                    )
                else:
                    tuition_fee.status = TuitionFeeStatusEnum.PAID.value

                    self.tuition_fee_repository.update(tuition_fee)

                    message = "Payment completed successfully"

                event = PaymentEventEnum.PAYMENT_SUCCESS.value

            else:
                payment.status = PaymentStatusEnum.FAILED.value

                event = PaymentEventEnum.PAYMENT_FAILED.value
                message = "Payment failed"

            payment.vnp_transaction_no = transaction_no
            payment.response_code = response_code

            self.payment_repository.update(payment)

            self.payment_log_repository.save(
                PaymentLog(
                    payment_id=payment.id,
                    event=event,
                    response_code=response_code,
                    transaction_no=transaction_no,
                    message=message
                )
            )

            self.db.commit()

            return {
                "RspCode": "00",
                "Message": "Confirm Success"
            }

        except Exception:
            self.db.rollback()

            return {
                "RspCode": "99",
                "Message": "Unknown error"
            }

    def get_payment_status(
        self,
        order_id: str,
        user_id: str
    ) -> dict:

        payment = self.payment_repository.find_by_order_id(order_id)

        if not payment or str(payment.user_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        return {
            "order_id": payment.order_id,
            "amount": payment.amount,
            "status": payment.status,
            "transaction_no": payment.vnp_transaction_no,
            "response_code": payment.response_code
        }
