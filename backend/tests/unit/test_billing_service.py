"""
Unit tests for Billing Service
TDD - Improving test coverage for billing_service.py
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.billing_service import BillingService
from app.db.models import Invoice, InvoiceStatus


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


