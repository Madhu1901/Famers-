Buyer user Side views.py
from django.shortcuts import render,HttpResponse, redirect
from django.contrib import messages
from .forms import BuyerUserRegistrationForm
from .models import BuyerUserRegistrationModel, BuyerCropCartModels,BuyerTransactionModels,BlockChainTransactionModel
from sellers.models import FarmersCropsModels
from .utility.BlockChainImpl import Blockchain
from django.db.models import Sum
import random

blockchain = Blockchain()
# Create your views here.
def BuyerUserRegisterActions(request):
    if request.method == 'POST':
        form = BuyerUserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = BuyerUserRegistrationForm()
            return render(request, 'BuyerUserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = BuyerUserRegistrationForm()
    return render(request, 'BuyerUserRegistrations.html', {'form': form})
def BuyerUserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = BuyerUserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                cartin = checkCartCount(loginid)
                return render(request, 'buyers/BuyerUserHome.html', {'count':cartin})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'BuyerLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'BuyerLogin.html', {})
def BuyerUserHome(request):
    loginid = request.session['loginid']
    cartin = checkCartCount(loginid)
    return render(request, 'buyers/BuyerUserHome.html', {'count':cartin})

def BuyerSearchProductsForm(request):
    loginid = request.session['loginid']
    cartin = checkCartCount(loginid)
    return render(request,"buyers/BuyerSearchProducts.html",{'count':cartin})

def BuyerSearchCropsAction(request):
    if request.method=='POST':
        crpname = request.POST.get('cropname')
        search_data = FarmersCropsModels.objects.filter(cropname__icontains=crpname)
        loginid = request.session['loginid']
        cartin = checkCartCount(loginid)
        return render(request, 'buyers/BuyerSearchResults.html',{'data':search_data,'count':cartin})



def BuyerAddCropsToCart(request):
    crop_id = request.GET.get('cropid')
    crop = FarmersCropsModels.objects.get(id=crop_id)
    sellername = crop.sellername
    cropname = crop.cropname
    price = crop.price
    description = crop.description
    file = crop.file
    buyerUser = request.session['loginid']
    buyeremail = request.session['email']
    cartStatus = 'waiting'
    BuyerCropCartModels.objects.create(buyerusername=buyerUser,buyeruseremail=buyeremail,sellername=sellername,cropname=cropname, description=description, price=price, file=file,status=cartStatus)
    print("Seller name ",sellername)
    search_data = FarmersCropsModels.objects.filter(cropname__icontains=cropname)
    cartin = checkCartCount(buyerUser)
    print("Cart Count = ",cartin)
    loginid = request.session['loginid']
    cartin = checkCartCount(loginid)
    return render(request, 'buyers/BuyerSearchResults.html', {'data': search_data,'count':cartin})


def checkCartCount(buyername):
    cartin = BuyerCropCartModels.objects.filter(buyerusername=buyername,status='waiting').count()
    return cartin


def BuyyerCheckCartData(request):
    buyerName =request.GET.get('buyerUser')
    data = BuyerCropCartModels.objects.filter(buyerusername=buyerName, status='waiting')
    return render(request,"buyers/BuyerCheckInCart.html",{'data':data})

def BuyerDeleteanItemfromCart(request):
    cropid = request.GET.get('cropid')
    BuyerCropCartModels.objects.filter(id=cropid).delete()
    buyerName = request.session['loginid']
    cartin = checkCartCount(buyerName)
    data = BuyerCropCartModels.objects.filter(buyerusername=buyerName, status='waiting')
    return render(request, "buyers/BuyerCheckInCart.html", {'data': data,'count':cartin})

def startBlockChainProcess(request):
    blockchain = Blockchain()
    t1 = blockchain.new_transaction("Satoshi", "Mike", '5 BTC')
    blockchain.new_block(12346)
    t2 = blockchain.new_transaction("Mike", "Satoshi", '1 BTC')
    t3 = blockchain.new_transaction("Satoshi", "Hal Finney", '5 BTC')
    blockchain.new_block(12345)
    print("Genesis block: ", blockchain.chain)
    return HttpResponse("Block Chain Started")

def BuyerTotalAmountCheckOut(request):
    buyerName = request.GET.get('buyername')
    cartstatuc = 'waiting'
    total_price = BuyerCropCartModels.objects.filter(buyerusername=buyerName, status='waiting').aggregate(Sum('price'))
    total_price = total_price['price__sum']
    print('Total Price ',total_price)
    bank = ('SBI Bank','Union Bank','ICICI Bank','Axis Bank','Canara Bank','HDFC Bank','FDI Bank','Chase Bank')
    recipient = random.choice(bank)
    return render(request, 'buyers/BuyerInitiateTransactionForm.html',{'buyername':buyerName,'totaPrice':total_price,'bank':recipient})

def StartBlockChainTransaction(request):
    if request.method=='POST':
        ## Block Chain Data
        buyername = request.POST.get('buyername')
        totalamount = request.POST.get('totalamount')
        recipientnmae = request.POST.get('recipientnmae')

        #Transaction Data
        cardnumber = request.POST.get('cardnumber')
        nameoncard = request.POST.get('nameoncard')
        cvv = request.POST.get('cvv')
        cardexpiry = request.POST.get('cardexpiry')

        t1 = blockchain.new_transaction(buyername, recipientnmae, totalamount)
        proofId = ''.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
        blockchain.new_block(int(proofId))
        print("Genesis block: ", blockchain.chain)
        print("T1 is ",t1)
        currentTrnx = blockchain.chain[-1]
        previousTranx = blockchain.chain[-2]
        ### Current Tranasction Details
        c_transactions = currentTrnx.get('transactions')
        c_tnx_Dict = c_transactions[0]

        c_index = currentTrnx.get('index')
        c_timestamp = currentTrnx.get('timestamp')
        c_sender = c_tnx_Dict.get('sender')
        c_recipient = c_tnx_Dict.get('recipient')
        c_amount = c_tnx_Dict.get('amount')
        c_proof = currentTrnx.get('proof')
        c_previous_hash = currentTrnx.get('previous_hash')

        c_dict_rslt = {'c_index':c_index,'c_timestamp':c_timestamp,'c_sender':c_sender,'c_recipient':c_recipient,'c_amount':c_amount,'c_proof':c_proof,'c_previous_hash':c_previous_hash}

        # previous Transaction
        p_dict_rslt = {}
        p_transactions = previousTranx.get('transactions')
        if(len(p_transactions)!=0):
            p_tnx_Dict = p_transactions[0]

            p_index = previousTranx.get('index')
            p_timestamp = previousTranx.get('timestamp')
            p_sender = p_tnx_Dict.get('sender')
            p_recipient = p_tnx_Dict.get('recipient')
            p_amount = p_tnx_Dict.get('amount')
            p_proof = previousTranx.get('proof')
            p_previous_hash = previousTranx.get('previous_hash')

            BuyerTransactionModels.objects.create(buyername=buyername, totalamount=totalamount,recipientname=recipientnmae,cradnumber=cardnumber,nameoncard=nameoncard,cvv=cvv, cardexpiry=cardexpiry)
            p_dict_rslt = {'p_index': p_index, 'p_timestamp': p_timestamp, 'p_sender': p_sender, 'p_recipient': p_recipient, 'p_amount': p_amount, 'p_proof': p_proof, 'p_previous_hash': p_previous_hash}
            BlockChainTransactionModel.objects.create(c_index=c_index,c_timestamp=c_timestamp,c_sender=c_sender,c_recipient=c_recipient, c_amount=c_amount,c_proof=c_proof,c_previous_hash=c_previous_hash,p_index=p_index, p_timestamp=p_timestamp,p_sender=p_sender,p_recipient=p_recipient,p_amount=p_amount,p_proof=p_proof,p_previous_hash=p_previous_hash)
            buyer_name = request.session['loginid']
            print('buyername =',buyer_name)
            qs = BuyerCropCartModels.objects.filter(buyerusername=buyer_name).update(status='purchased')
        else:
            BuyerTransactionModels.objects.create(buyername=buyername, totalamount=totalamount,
                                                  recipientname=recipientnmae, cradnumber=cardnumber,
                                                  nameoncard=nameoncard, cvv=cvv, cardexpiry=cardexpiry)

            BlockChainTransactionModel.objects.create(c_index=c_index, c_timestamp=c_timestamp, c_sender=c_sender,
                                                      c_recipient=c_recipient, c_amount=c_amount, c_proof=c_proof,
                                                      c_previous_hash=c_previous_hash, p_index='p_index',
                                                      p_timestamp='p_timestamp', p_sender='p_sender',
                                                      p_recipient="p_recipient", p_amount="p_amount", p_proof="p_proof",
                                                      p_previous_hash="p_previous_hash")
            buyer_name = request.session['loginid']
            print('buyername =', buyer_name)
            qs = BuyerCropCartModels.objects.filter(buyerusername=buyer_name).update(status='purchased')
        return render(request, 'buyers/TransactionResults.html',{'c_dict_rslt':c_dict_rslt,'p_dict_rslt':p_dict_rslt})

def BuyerViewPurchasedDetails(request):
    buyer_name = request.session['loginid']
    cartin = checkCartCount(buyer_name)
    data = BuyerCropCartModels.objects.filter(buyerusername=buyer_name,status='purchased')
    return render(request, 'buyers/BuyersViewPurchasedData.html',{'data':data,'count':cartin})

def BuyerViewTransactinDetails(request):
    bd_name = request.session['loginid']
    print('buyer_name',bd_name)
    data = BuyerTransactionModels.objects.filter(buyername = ' '+bd_name)
    cartin = checkCartCount(bd_name)
    return render(request, 'buyers/BuyersViewTransactionDetails.html',{'data':data,'count':cartin})
BlockChain.py
import hashlib
import json
from time import time


class Blockchain(object):
    def _init_(self):
        self.chain = []
        self.pending_transactions = []

        self.new_block(previous_hash="The Times 03/Oct/2020 A Study of Blockchain Technology in Farmer’s Portal.",proof=100)

    # Create a new block listing key/value pairs of block information in a JSON object. Reset the list of pending transactions & append the newest block to the chain.

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.pending_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.pending_transactions = []
        self.chain.append(block)

        return block

    # Search the blockchain for the most recent block.

    @property
    def last_block(self):
        return self.chain[-1]

    # Add a transaction with relevant info to the 'blockpool' - list of pending tx's.

    def new_transaction(self, sender, recipient, amount):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.pending_transactions.append(transaction)
        return self.last_block['index'] + 1

    # receive one block. Turn it into a string, turn that into Unicode (for hashing). Hash with SHA256 encryption, then translate the Unicode into a hexidecimal string.

    def hash(self, block):
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()

        raw_hash = hashlib.sha256(block_string)
        hex_hash = raw_hash.hexdigest()

        return hex_hash

Buyer Models:
from django.db import models

# Create your models here.
class BuyerUserRegistrationModel(models.Model):
    name = models.CharField(max_length=100)
    loginid = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    mobile = models.CharField(unique=True, max_length=100)
    email = models.CharField(unique=True, max_length=100)
    locality = models.CharField(max_length=100)
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    def _str_(self):
        return self.loginid

    class Meta:
        db_table = 'BuyersRegistrations'



class BuyerCropCartModels(models.Model):
    buyerusername = models.CharField(max_length=100)
    buyeruseremail = models.CharField(max_length=100)
    sellername = models.CharField(max_length=100)
    cropname = models.CharField(max_length=100)
    description = models.CharField(max_length=100000)
    price = models.FloatField()
    file = models.FileField(upload_to='files/')
    cdate = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def _str_(self):
        return self.buyerusername

    class Meta:
        db_table = "BuyerCartTable"


class BuyerTransactionModels(models.Model):
    buyername = models.CharField(max_length=100)
    totalamount = models.FloatField()
    recipientname = models.CharField(max_length=100)
    cradnumber = models.IntegerField()
    nameoncard = models.CharField(max_length=100)
    cvv = models.IntegerField()
    cardexpiry = models.CharField(max_length=200)
    trnx_date = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        #return self.id
        return self.buyername

    class Meta:
        db_table = "BuyerTransactionTable"

class BlockChainTransactionModel(models.Model):
    c_index = models.CharField(max_length=100)
    c_timestamp = models.CharField(max_length=100)
    c_sender = models.CharField(max_length=100)
    c_recipient = models.CharField(max_length=100)
    c_amount = models.CharField(max_length=100)
    c_proof = models.CharField(max_length=100)
    c_previous_hash = models.CharField(max_length=100)
    p_index = models.CharField(max_length=100)
    p_timestamp = models.CharField(max_length=100)
    p_sender = models.CharField(max_length=100)
    p_recipient = models.CharField(max_length=100)
    p_amount = models.CharField(max_length=100)
    p_proof = models.CharField(max_length=100)
    p_previous_hash = models.CharField(max_length=100)

    def _str_(self):
        return self.id

    class Meta:
        db_table = "BlockChainTransactiontable"

Sellers side views.py
from django.shortcuts import render,HttpResponse
from django.contrib import messages
from .forms import SellerUserRegistrationForm
from .models import SellerUserRegistrationModel, FarmersCropsModels
from django.core.files.storage import FileSystemStorage
from buyers.models import BuyerCropCartModels

# Create your views here.
def SellerUserRegisterActions(request):
    if request.method == 'POST':
        form = SellerUserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = SellerUserRegistrationForm()
            return render(request, 'SellerUserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = SellerUserRegistrationForm()
    return render(request, 'SellerUserRegistrations.html', {'form': form})
def SellerUserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = SellerUserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'sellers/SellerUserHome.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'SellerLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'SellerLogin.html', {})
def SellerUserHome(request):
    return render(request, 'sellers/SellerUserHome.html', {})

def SellerAddItemsForm(request):
    return render(request, 'sellers/SellerAddItems.html',{})

def SellerAddItemsAction(request):
    if request.method=='POST':
        cropname = request.POST.get('cropname')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image_file = request.FILES['file']

        # let's check if it is a csv file
        if not image_file.name.endswith('.jpg'):
            messages.error(request, 'THIS IS NOT A JPG  FILE')

        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        detect_filename = fs.save(image_file.name, image_file)
        uploaded_file_url = fs.url(filename)
        loginid = request.session['loginid']
        email = request.session['email']
        FarmersCropsModels.objects.create(sellername=loginid, selleremail=email, cropname=cropname,price=price, description=description,file=uploaded_file_url)
        messages.success(request, 'Crop Data Addedd Success')
        return render(request, 'sellers/SellerAddItems.html', {})

def SellersCommodities(request):
    loginid = request.session['loginid']
    data = FarmersCropsModels.objects.filter(sellername=loginid)
    return render(request, 'sellers/SellersCommoditiesData.html',{'data':data})

def SellerUpdateProducts(request):
    cropid = request.GET.get('cropid')
    data = FarmersCropsModels.objects.get(id=cropid)
    return render(request, 'sellers/CropsUpdatesbySeller.html', {'data': data})

    return HttpResponse("Update products Working Success")

def SellerDeleteProducts(request):
    cropid = request.GET.get('cropid')
    FarmersCropsModels.objects.filter(id=cropid).delete()
    loginid = request.session['loginid']
    data = FarmersCropsModels.objects.filter(sellername=loginid)
    return render(request, 'sellers/SellersCommoditiesData.html', {'data': data})


def SellerCropUpdateAction(request):
    #MyModel.objects.filter(pk=some_value).update(field1='some value')
    cropname = request.POST.get('cropname')
    price = request.POST.get('price')
    cropid = request.POST.get('cropid')
    description = request.POST.get('description')
    image_file = request.FILES['file']
    # let's check if it is a csv file
    if not image_file.name.endswith('.jpg'):
        messages.error(request, 'THIS IS NOT A JPG  FILE')

    fs = FileSystemStorage()
    filename