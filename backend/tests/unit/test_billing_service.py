"""
Unit tests for Billing Service
TDD - Improving test coverage for billing_service.py
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.billing_service import BillingService
from app.db.models import Invoice, InvoiceStatus
from app.db.schemas import InvoiceUpdate


class TestGetInvoiceById:
    """Unit tests for get_invoice_by_id method"""

    def test_get_invoice_not_found(self):
        """Returns None when invoice not found"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db

            result = service.get_invoice_by_id("nonexistent", "user-123")

            assert result is None

    def test_get_invoice_no_access(self):
        """Returns None when user has no access"""
        mock_db = MagicMock()
        mock_invoice = MagicMock(spec=Invoice)
        mock_invoice.lawyer_id = "other-lawyer"
        mock_invoice.client_id = "other-client"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_invoice

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db

            result = service.get_invoice_by_id("invoice-123", "user-123")

            assert result is None


class TestDeleteInvoice:
    """Unit tests for delete_invoice method"""

    def test_delete_invoice_not_found(self):
        """Returns False when invoice not found"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db

            result = service.delete_invoice("nonexistent", "lawyer-123")

            assert result is False


class TestUpdateInvoice:
    """Unit tests for update_invoice method"""

    def test_update_invoice_not_found(self):
        """Returns None when invoice not found"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db

            result = service.update_invoice("nonexistent", {}, "lawyer-123")

            assert result is None


class TestDeleteInvoiceSuccess:
    """Unit tests for delete_invoice success path"""

    def test_delete_invoice_success(self):
        """Successfully deletes invoice"""
        mock_db = MagicMock()
        mock_invoice = MagicMock(spec=Invoice)
        mock_invoice.id = "invoice-123"
        mock_invoice.lawyer_id = "lawyer-123"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_invoice

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db

            result = service.delete_invoice("invoice-123", "lawyer-123")

            assert result is True
            mock_db.delete.assert_called_once_with(mock_invoice)
            mock_db.commit.assert_called_once()


class TestCreateInvoice:
    """Unit tests for create_invoice method"""

    def test_create_invoice_no_case_access(self):
        """Returns None when lawyer has no case access"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db

            mock_data = MagicMock()
            mock_data.case_id = "case-123"
            mock_data.client_id = "client-123"
            mock_data.amount = "100000"
            mock_data.description = "Test invoice"
            mock_data.due_date = datetime.now(timezone.utc)

            result = service.create_invoice("lawyer-123", mock_data)

            assert result is None


class TestProcessPayment:
    """Unit tests for process_payment method"""

    def test_process_payment_invoice_not_found(self):
        """Returns None when invoice not found"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db

            result = service.process_payment("invoice-123", "client-123", "credit_card")

            assert result is None

    def test_process_payment_already_paid(self):
        """Returns invoice when already paid"""
        mock_db = MagicMock()
        mock_invoice = MagicMock(spec=Invoice)
        mock_invoice.id = "invoice-123"
        mock_invoice.client_id = "client-123"
        mock_invoice.lawyer_id = "lawyer-123"
        mock_invoice.case_id = "case-123"
        mock_invoice.amount = "100000"
        mock_invoice.description = "Test"
        mock_invoice.status = InvoiceStatus.PAID
        mock_invoice.due_date = datetime.now(timezone.utc)
        mock_invoice.paid_at = datetime.now(timezone.utc)
        mock_invoice.created_at = datetime.now(timezone.utc)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_invoice

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db
            service._to_invoice_out = MagicMock(return_value=MagicMock())

            result = service.process_payment("invoice-123", "client-123", "credit_card")

            assert result is not None
            service._to_invoice_out.assert_called_once_with(mock_invoice)

    def test_process_payment_success(self):
        """Successfully processes payment and updates invoice status"""
        mock_db = MagicMock()
        mock_invoice = MagicMock(spec=Invoice)
        mock_invoice.id = "invoice-123"
        mock_invoice.client_id = "client-123"
        mock_invoice.lawyer_id = "lawyer-123"
        mock_invoice.case_id = "case-123"
        mock_invoice.amount = "100000"
        mock_invoice.description = "Test"
        mock_invoice.status = InvoiceStatus.PENDING  # Not paid yet
        mock_invoice.due_date = datetime.now(timezone.utc)
        mock_invoice.paid_at = None
        mock_invoice.created_at = datetime.now(timezone.utc)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_invoice

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db
            service._to_invoice_out = MagicMock(return_value=MagicMock())

            service.process_payment("invoice-123", "client-123", "credit_card")

            # Should update status to PAID
            assert mock_invoice.status == InvoiceStatus.PAID
            assert mock_invoice.paid_at is not None
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_invoice)
            service._to_invoice_out.assert_called_once()


class TestGetInvoicesForLawyer:
    """Unit tests for get_invoices_for_lawyer method"""

    def test_get_invoices_invalid_status_ignored(self):
        """Invalid status is ignored (ValueError caught)"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db
            service._calculate_total_by_status = MagicMock(return_value=0)

            # Call with invalid status - should not raise, just ignore
            result = service.get_invoices_for_lawyer(
                "lawyer-123",
                status="INVALID_STATUS",
                page=1,
                limit=10
            )

            assert result is not None
            assert result.total == 0


class TestUpdateInvoiceSuccess:
    """Unit tests for update_invoice success paths"""

    def test_update_invoice_with_all_fields(self):
        """Updates invoice with all fields"""
        mock_db = MagicMock()
        mock_invoice = MagicMock(spec=Invoice)
        mock_invoice.id = "invoice-123"
        mock_invoice.lawyer_id = "lawyer-123"
        mock_invoice.case_id = "case-123"
        mock_invoice.client_id = "client-123"
        mock_invoice.amount = "100000"
        mock_invoice.description = "Original"
        mock_invoice.status = InvoiceStatus.PENDING
        mock_invoice.due_date = datetime.now(timezone.utc)
        mock_invoice.paid_at = None
        mock_invoice.created_at = datetime.now(timezone.utc)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_invoice

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db
            service._to_invoice_out = MagicMock(return_value=MagicMock())

            update_data = InvoiceUpdate(
                amount="200000",
                description="Updated description",
                status=InvoiceStatus.PAID,
                due_date=datetime(2024, 12, 31, tzinfo=timezone.utc)
            )

            service.update_invoice("invoice-123", "lawyer-123", update_data)

            # Check fields were updated
            assert mock_invoice.amount == "200000"
            assert mock_invoice.description == "Updated description"
            assert mock_invoice.status == InvoiceStatus.PAID
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_invoice)
            service._to_invoice_out.assert_called_once()


class TestCalculateTotalByStatus:
    """Unit tests for _calculate_total_by_status method"""

    def test_calculate_total_exception_fallback(self):
        """Falls back to manual calculation on database exception"""
        mock_db = MagicMock()

        # Make the first query (sum) raise an exception
        mock_db.query.return_value.filter.return_value.scalar.side_effect = Exception("DB Error")

        # Set up fallback query - return mock invoices
        mock_invoice1 = MagicMock()
        mock_invoice1.amount = "100000"
        mock_invoice2 = MagicMock()
        mock_invoice2.amount = "50000"

        # Create separate mock for the fallback query
        fallback_query = MagicMock()
        fallback_query.all.return_value = [mock_invoice1, mock_invoice2]

        # Set up query chain for fallback
        call_count = [0]

        def query_side_effect(*args):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call - for sum query, raise exception
                result = MagicMock()
                result.filter.return_value.scalar.side_effect = Exception("DB Error")
                return result
            else:
                # Second call - for fallback query
                result = MagicMock()
                result.filter.return_value.all.return_value = [mock_invoice1, mock_invoice2]
                return result

        mock_db.query.side_effect = query_side_effect

        with patch.object(BillingService, '__init__', lambda x, y: None):
            service = BillingService(mock_db)
            service.db = mock_db

            result = service._calculate_total_by_status("lawyer-123", InvoiceStatus.PENDING)

            # Should fall back and calculate sum manually
            assert result == 150000


