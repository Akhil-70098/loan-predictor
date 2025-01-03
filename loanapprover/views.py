from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict
import pickle
from django.shortcuts import render, HttpResponseRedirect

@dataclass
class LoanRequest:
    model_data: List[int]
    interest_data: List[int]

class LoanStrategy(ABC):
    @abstractmethod
    def process(self, request: LoanRequest) -> dict:
        pass

class MLModelLoanStrategy(LoanStrategy):
    def __init__(self):
        self.loan_model = pickle.load(open('mlModel.pickle', 'rb'))
        self.interest_model = pickle.load(open('interest.pickle', 'rb'))

    def _get_rejection_reasons(self, data: List[int]) -> List[str]:
        reasons = []
        if data[8] == 0:
            reasons.append("You have pending loans and they must be cleared.")
        if data[3] == 1:
            reasons.append("You must be continuously employed.")
        if data[13] == 1:
            reasons.append("Your property in rural area cannot be accepted as collateral.")
        if data[4] * data[7] // 30 < data[6]:
            reasons.append("Applicant income is too low.")
        return reasons

    def _get_bank_offer(self, interest_rate: float) -> str:
        if interest_rate <= 2.5:
            return "Bank 1 is ready to give loan."
        if interest_rate <= 4.5:
            return "Bank 2 is ready to give loan."
        return "Bank 3 is ready to give loan."

    def process(self, request: LoanRequest) -> dict:
        if request.model_data[4] <= 0 and request.model_data[5] <= 0:
            return {
                'loan_result': "Either applicant or co-applicant income must be greater than zero.",
                'is_approved': 0,
                'interest_result': '',
                'bank_offer': '',
                'reasons': []
            }

        if request.model_data[6] <= 0:
            return {
                'loan_result': "Loan amount must be greater than zero.",
                'is_approved': 0,
                'interest_result': '',
                'bank_offer': '',
                'reasons': []
            }

        loan_prediction = self.loan_model.predict([request.model_data])[0]
        interest_rate = min(8, self.interest_model.predict([request.interest_data])[0])

        if loan_prediction == 1:
            return {
                'loan_result': "Loan approved.",
                'is_approved': 1,
                'interest_result': f"Interest rate: {round(interest_rate, 2)}",
                'bank_offer': self._get_bank_offer(interest_rate),
                'reasons': []
            }
        
        return {
            'loan_result': "Loan not approved.",
            'is_approved': 0,
            'interest_result': '',
            'bank_offer': '',
            'reasons': self._get_rejection_reasons(request.model_data)
        }

class LoanProcessor:
    def __init__(self, strategy: LoanStrategy):
        self.strategy = strategy

    @staticmethod
    def process_dependents(dependents: str) -> List[int]:
        mapping = {
            "0": [1,0,0,0], "1": [0,1,0,0],
            "2": [0,0,1,0], "3+": [0,0,0,1]
        }
        return mapping.get(dependents, [0,0,0,0])

    @staticmethod
    def process_property(property_type: str) -> List[int]:
        mapping = {
            "rural": [1,0,0],
            "semi urban": [0,1,0],
            "urban": [0,0,1]
        }
        return mapping.get(property_type, [0,0,0])

    def process_loan(self, request_data: Dict) -> dict:
        model_data = [
            int(request_data['gender']),
            int(request_data['marital']),
            int(request_data['education']),
            int(request_data['selfemployment']),
            int(request_data['income']),
            int(request_data['co-income']),
            int(request_data['loan-amount']),
            int(request_data['loan-term']),
            int(request_data['credit_history'])
        ]
        model_data.extend(self.process_dependents(request_data['dependents']))
        model_data.extend(self.process_property(request_data['property']))

        interest_data = [
            int(request_data['income']) if int(request_data['income']) > 0 
            else int(request_data['co-income']),
            int(request_data['loan-amount'])
        ]

        loan_request = LoanRequest(model_data, interest_data)
        return self.strategy.process(loan_request)

# Django views
def index(request):
    if request.method == 'POST':
        processor = LoanProcessor(MLModelLoanStrategy())
        result = processor.process_loan(request.POST)
        request.session['loan_result'] = result
        return HttpResponseRedirect('http://localhost:8000/result/')
    return render(request, 'index.html')

def result(request):
    result = request.session.get('loan_result', {})
    if not result:
        return render(request, 'result.html', {
            'result': 'Error: Missing data.',
            'result2': '',
            'result3': '',
            'gear': [],
            'isapproved': 0
        })

    return render(request, 'result.html', {
        'result': result['loan_result'],
        'interestresult': result['interest_result'],
        'bankoffer': result['bank_offer'],
        'gear': result['reasons'],
        'isapproved': result['is_approved']
    })