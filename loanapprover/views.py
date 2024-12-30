from django.shortcuts import render
import pickle
from django.http import HttpResponseRedirect
# Create your views here.
list1=[]
list5=[[]]
list3=[]
era=[]
koro=0
temp = pickle.load(open('mlModel.pkl','rb'))
temp2 = pickle.load(open('interest.pkl','rb'))
def insert(list1):
    list2=[]
    list2.append(list1)
    return list2
def reasons(list5):
    ear=[]
    if list5[0][8]==0:
        ear.append("You have pending loans and they must be cleared to get the loan")        
    if list5[0][3]==1:
        ear.append("You must be continuously employed to clear the loan as you have your own business which cannot give appropriate revenue from time to time")
    if list5[0][13]==1:
        ear.append("Your property is in rural area which cannot be accepted as collateral.Better if you have your property in semi urban or urban area")
    if list5[0][4]*list5[0][7]//30 < list5[0][6]:
        ear.append("Applicant income is low and cannot pay the loan")
    return ear
def index(request):
    if request.method == 'POST':
            print('Validation Success')
            print("Name: "+request.POST['name'])
            print("Email: "+request.POST['mail'])
            list1.append(int(request.POST['gender']))
            list1.append(int(request.POST['marital']))
            list1.append(int(request.POST['education']))
            list1.append(int(request.POST['selfemployment']))
            list1.append(int(request.POST['income']))
            list1.append(int(request.POST['co-income']))
            list1.append(int(request.POST['loan-amount']))
            list1.append(int(request.POST['loan-term']))
            list1.append(int(request.POST['credit_history']))
            if request.POST['dependents'] == "0":
                list1.append(1)
                list1.append(0)
                list1.append(0)
                list1.append(0)
            elif request.POST['dependents'] == "1":
                list1.append(0)
                list1.append(1)
                list1.append(0)
                list1.append(0)
            elif request.POST['dependents'] == "2":
                list1.append(0)
                list1.append(0)
                list1.append(1)
                list1.append(0)
            else:
                list1.append(0)
                list1.append(0)
                list1.append(0)
                list1.append(1)

            if request.POST['property'] == "rural":
                list1.append(1)
                list1.append(0)
                list1.append(0)
            elif request.POST['property'] == "semi urban":
                list1.append(0)
                list1.append(1)
                list1.append(0)
            else:
                list1.append(0)
                list1.append(0)
                list1.append(1)
            if int(request.POST['income'])>0:
                list3.append(int(request.POST['income']))
            else:
                list3.append(int(request.POST['co-income']))
            list3.append(int(request.POST['loan-amount']))
            return HttpResponseRedirect('http://localhost:8000/result/')
    return render(request,'index.html')

def result(request):
        global era
        global koro
        list2 = insert(list1)
        pump = temp.predict(list2)
        length = len(list2)
        tupu = pump[length-1]
        if list2[0][4]<=0 and list2[0][5]<=0:
            res = "Either applicant income or co applicant Income must be greater than zero"
        elif list2[0][6]<=0:
            res = "Loan amount must be greater than zero"
        else:
            koro=1
            if pump[length-1]==1:
                res = "Loan approved"
            else:
                res = "Loan not approved"
                era = reasons(list2)
        print(list2)
        list1.clear()
        list4 = insert(list3)
        pump2 = temp2.predict(list4)
        length = len(list4)
        if pump2[length-1]>8:
            pump2[length-1]=8
        res2 = "A loan will be given with an interest rate of "+ str(round(pump2[length-1],2))
        if pump2[length-1]<=2.5:
            res3 = " Bank 1 is ready to give loan nearly to the mentioned interest"
        elif pump2[length-1]>2.5 and pump2[length-1]<=4.5:
             res3 = " Bank 2 is ready to give loan nearly to the mentioned interest"
        else:
            res3 = "Bank 3 is ready to give loan nearly to the mentioned interest"
        list3.clear()
        return render(request,'result.html',{'result':res,'result2':res2,'result3':res3,'tuput':tupu,'gear':era,'korot':koro})
