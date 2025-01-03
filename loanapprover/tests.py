# Create your tests here.
import unittest
from unittest.mock import Mock, patch
from django.test import TestCase, RequestFactory
from django.http import HttpResponseRedirect
from .views import *


class TestLoanProcessor(TestCase):
    def setUp(self):
        self.processor = LoanProcessor(MLModelLoanStrategy())
        self.valid_request_data = {
            'gender': '1',
            'marital': '1',
            'education': '1',
            'selfemployment': '0',
            'income': '5000',
            'co-income': '2000',
            'loan-amount': '10000',
            'loan-term': '12',
            'credit_history': '1',
            'dependents': '1',
            'property': 'urban'
        }

    def test_process_dependents(self):
        self.assertEqual(self.processor.process_dependents("0"), [1, 0, 0, 0])
        self.assertEqual(self.processor.process_dependents("1"), [0, 1, 0, 0])
        self.assertEqual(self.processor.process_dependents(
            "invalid"), [0, 0, 0, 0])

    def test_process_property(self):
        self.assertEqual(self.processor.process_property("rural"), [1, 0, 0])
        self.assertEqual(self.processor.process_property("urban"), [0, 0, 1])
        self.assertEqual(self.processor.process_property("invalid"), [0, 0, 0])

    @patch('pickle.load')
    def test_loan_processing_approved(self, mock_pickle):
        mock_loan_model = Mock()
        mock_loan_model.predict.return_value = [1]
        mock_interest_model = Mock()
        mock_interest_model.predict.return_value = [2.5]

        mock_pickle.side_effect = [mock_loan_model, mock_interest_model]

        result = self.processor.process_loan(self.valid_request_data)

        self.assertEqual(result['loan_result'], "Loan approved.")
        self.assertEqual(result['is_approved'], 1)
        self.assertTrue('Interest rate' in result['interest_result'])

    def test_invalid_income(self):
        invalid_data = self.valid_request_data.copy()
        invalid_data['income'] = '0'
        invalid_data['co-income'] = '0'

        result = self.processor.process_loan(invalid_data)

        self.assertEqual(result['is_approved'], 0)
        self.assertTrue(
            'income must be greater than zero' in result['loan_result'])


class TestMLModelLoanStrategy(TestCase):
    def setUp(self):
        self.strategy = MLModelLoanStrategy()

    def test_get_rejection_reasons(self):
        test_data = [0] * 14
        test_data[8] = 0  # pending loans
        test_data[3] = 1  # self employed

        reasons = self.strategy._get_rejection_reasons(test_data)

        self.assertTrue(any('pending loans' in reason.lower()
                        for reason in reasons))
        self.assertTrue(any('continuously employed' in reason.lower()
                        for reason in reasons))

    def test_get_bank_offer(self):
        self.assertTrue('Bank 1' in self.strategy._get_bank_offer(2.0))
        self.assertTrue('Bank 2' in self.strategy._get_bank_offer(3.5))
        self.assertTrue('Bank 3' in self.strategy._get_bank_offer(5.0))


class TestViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_index_get(self):
        request = self.factory.get('/')
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def test_index_post(self):
        request = self.factory.post('/', {
            'gender': '1',
            'marital': '1',
            'education': '1',
            'selfemployment': '0',
            'income': '5000',
            'co-income': '2000',
            'loan-amount': '10000',
            'loan-term': '12',
            'credit_history': '1',
            'dependents': '1',
            'property': 'urban'
        })
        request.session = {}

        response = index(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_result_missing_data(self):
        request = self.factory.get('/result/')
        request.session = {}

        response = result(request)
        self.assertContains(response, 'Error: Missing data.')


if __name__ == '__main__':
    unittest.main()
