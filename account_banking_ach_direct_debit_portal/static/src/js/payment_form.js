import PaymentForm from "@payment/js/payment_form";

PaymentForm.include({
    _prepareTransactionRouteParams() {
        const transactionRouteParams = this._super(...arguments);
        transactionRouteParams.invoices = JSON.parse(this.paymentContext.invoices || "[]");
        transactionRouteParams.surcharge_amount = parseFloat(this.paymentContext.surchargeAmount) ? this.paymentContext.surchargeAmount : 0.0;
        return transactionRouteParams;
    },
});
