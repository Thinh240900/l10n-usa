import {patch} from "@web/core/utils/patch";
import PaymentForm from "@payment/js/payment_form";

patch(PaymentForm.prototype, {
    _prepareTransactionRouteParams() {
        const transactionRouteParams = super._prepareTransactionRouteParams(
            ...arguments
        );
        transactionRouteParams.invoices = JSON.parse(
            this.paymentContext.invoices || "[]"
        );
        transactionRouteParams.surcharge_amount = parseFloat(
            this.paymentContext.surchargeAmount
        )
            ? this.paymentContext.surchargeAmount
            : 0.0;
        return transactionRouteParams;
    },
});
