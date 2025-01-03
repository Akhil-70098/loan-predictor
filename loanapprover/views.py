from django.shortcuts import render
import pickle
from django.http import HttpResponseRedirect

# Load models
loan_model = pickle.load(open('mlModel.pickle', 'rb'))
interest_model = pickle.load(open('interest.pickle', 'rb'))

# Utility function to calculate reasons for loan rejection
def get_reasons(result):
    reasons = []
    if result[8] == 0:
        reasons.append("You have pending loans and they must be cleared to get the loan.")
    if result[3] == 1:
        reasons.append("You must be continuously employed to clear the loan as you have your own business which cannot give appropriate revenue from time to time.")
    if result[13] == 1:
        reasons.append("Your property is in a rural area which cannot be accepted as collateral. Better if you have your property in a semi-urban or urban area.")
    if result[4] * result[7] // 30 < result[6]:
        reasons.append("Applicant income is low and cannot pay the loan.")
    return reasons

# Utility function to process dependents
def process_dependents(dependents):
    dependents_mapping = {
        "0": [1, 0, 0, 0],
        "1": [0, 1, 0, 0],
        "2": [0, 0, 1, 0],
        "3+": [0, 0, 0, 1]
    }
    return dependents_mapping.get(dependents, [0, 0, 0, 0])

# Utility function to process property type
def process_property(property_type):
    property_mapping = {
        "rural": [1, 0, 0],
        "semi urban": [0, 1, 0],
        "urban": [0, 0, 1]
    }
    return property_mapping.get(property_type, [0, 0, 0])

def index(request):
    if request.method == 'POST':
        model_data = [
            int(request.POST['gender']),
            int(request.POST['marital']),
            int(request.POST['education']),
            int(request.POST['selfemployment']),
            int(request.POST['income']),
            int(request.POST['co-income']),
            int(request.POST['loan-amount']),
            int(request.POST['loan-term']),
            int(request.POST['credit_history'])
        ]
        model_data.extend(process_dependents(request.POST['dependents']))
        model_data.extend(process_property(request.POST['property']))

        interest_data = [
            int(request.POST['income']) if int(request.POST['income']) > 0 else int(request.POST['co-income']),
            int(request.POST['loan-amount'])
        ]
        
        request.session['model_data'] = model_data
        request.session['interest_data'] = interest_data

        return HttpResponseRedirect('http://localhost:8000/result/')
    return render(request, 'index.html')

def result(request):
    model_data = request.session.get('model_data', [])
    interest_data = request.session.get('interest_data', [])
    result_list = [model_data]
    
    if not model_data or not interest_data:
        return render(request, 'result.html', {'result': 'Error: Missing data.', 'result2': '', 'result3': '', 'gear': [], 'isapproved': 0})

    loan_prediction = loan_model.predict(result_list)[0]
    interest_prediction = interest_model.predict([interest_data])[0]

    if interest_prediction > 8:
        interest_prediction = 8

    reasons_list = []
    if model_data[4] <= 0 and model_data[5] <= 0:
        loan_result = "Either applicant income or co-applicant Income must be greater than zero."
        is_approved = 0
    elif model_data[6] <= 0:
        loan_result = "Loan amount must be greater than zero."
        is_approved = 0
    else:
        if loan_prediction == 1:
            loan_result = "Loan approved."
            is_approved = 1
        else:
            loan_result = "Loan not approved."
            is_approved = 0
            reasons_list = get_reasons(model_data)

    interest_result = f"A loan will be given with an interest rate of {round(interest_prediction, 2)}"
    if interest_prediction <= 2.5:
        bank_offer = "Bank 1 is ready to give loan nearly to the mentioned interest."
    elif interest_prediction <= 4.5:
        bank_offer = "Bank 2 is ready to give loan nearly to the mentioned interest."
    else:
        bank_offer = "Bank 3 is ready to give loan nearly to the mentioned interest."

    return render(request, 'result.html', {
        'result': loan_result,
        'interestresult': interest_result,
        'bankoffer': bank_offer,
        'gear': reasons_list,
        'isapproved': is_approved
    })
