from django.shortcuts import render, redirect, HttpResponse
from .models import User_data  # Import the model

from django.shortcuts import render, get_object_or_404, redirect

# report generation
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
import uuid
from datetime import datetime


# View for the homepage
def index(request):
    context = "yek key msg se show kr rha hai "
    return render(request, "index.html", {"key":context})


# ------------------------------------------------------------------------------------------------------------------------

# View for the signup page
def signup(request):
    if request.method == "GET":
        return render(request, "signup.html")
    
    else:
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Check if email already exists in the database
        if User_data.objects.filter(email=email).exists():
            msg = "Email already exists"
            return render(request, "signup.html", {"key": msg})
        else:
            # Create a new user and save to the database
            ob = User_data(username=username, email=email, password=password)
            ob.save()
            return redirect("/login")

# ------------------------------------------------------------------------------------------------------------------------
# View for the login page
def login(request):
    msg = ""  # Initialize msg variable
    if request.method == "POST":
        email = request.POST["email"]  
        password = request.POST["password"] 
        print(email, password)
        
        if User_data.objects.filter(email=email).exists():
            if User_data.objects.filter(email=email, password=password).exists():
                request.session["email"] = email
                return redirect("/profile")
            else:
                msg = "Password is incorrect"
                return render(request, "login.html", {"key": msg})
        else:
            msg = "Email is invalid or incorrect"
            return render(request, "login.html", {"key": msg})
    
    return render(request, "login.html", {"key": msg})  # Corrected template

# ------------------------------------------------------------------------------------------------------------------------
# View for the profile page
def profile(request):
    if "email" in request.session:
        email = request.session.get("email")
        print(email)

        data = User_data.objects.filter(email=email)
        print(data)

        return render(request, "profile.html", {"data": data})

    else:
        msg = "Please log in again."
        return render(request, "login.html", {"key": msg})



# ------------------------------------------------------------------------------------------------------------------------
# View for the logout page
def logout(request):
    if "email" in request.session:
        del request.session["email"]
        return redirect("/login")
    else:
        return redirect("/login")

# ------------------------------------------------------------------------------------------------------------------------
# View for the update page
def update(request):
    if request.method == "POST":
        # id=request.POST.get("ID")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        User_data.objects.filter(email=email).update(username=username, password=password)
        return redirect("/login")
    else:
        if "email" in request.session:
            email = request.session.get("email")
            data = User_data.objects.filter(email=email)
            return render(request, "update.html", {"data": data})

        else:
            return HttpResponse("Please log in again")

# ------------------------------------------------------------------------------------------------------------------------
def delete(request):
    if "email" in request.session:
        email = request.session.get("email")
        ob=User_data.objects.filter(email=email)
        ob.delete()
        return redirect("/login")
    else:
        return HttpResponse("Please login again")
    
    # ------------------------------------------------------------------------------------------------------------------------


def datainsight(request):
    return render(request, 'datainsight.html')

def aboutus(request):
    return render(request, 'aboutus.html')

def contactus(request):
    return render(request, 'contactus.html')

# ------------------------------------------------------------------------------------------------------------------------
# def forecasting(request):
#     # Load your disease data
#     data = {
#         'Disease': ['Dengue', 'Malaria', 'Typhoid'],
#         'Cases': [1200, 850, 430],
#         'Deaths': [12, 9, 4]
#     }
#     df = pd.DataFrame(data)

#     # Pass the data to the template
#     context = {
#         'disease_data': df.to_dict(orient='records')
#     }
#     return render(request, 'forecasting.html', context)


def forecasting(request):
    # Your forecasting logic here
    return render(request, 'forecasting.html')

# ------------------------------------------------------------------------------------------------------------------------
# Report generation view
# def generate_report(request, disease):
#     template_path = 'report_template.html'  # Use standalone template
#     context = {
#         'disease': disease.capitalize(),
#         'report_id': str(uuid.uuid4()),
#         'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     }

#     # Render template to HTML
#     template = get_template(template_path)
#     html = template.render(context)

#     # Create PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="{disease}_report.pdf"'

#     result = BytesIO()
#     pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=result)

#     if not pdf.err:
#         response.write(result.getvalue())
#         return response
#     else:
#         return HttpResponse("Error generating PDF", status=500)


def generate_report(request, disease):
    # Unique ID and timestamp
    report_id = str(uuid.uuid4())[:8]
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Disease-specific data
    content = {
        'malaria': {
            'causes': 'Caused by Plasmodium parasites spread through mosquito bites.',
            'prevention': 'Use mosquito nets, repellents, and remove standing water.',
            'impact': 'Severe outbreaks in tropical and subtropical regions.',
        },
        'dengue': {
            'causes': 'Caused by Dengue virus spread through Aedes mosquitoes.',
            'prevention': 'Prevent mosquito breeding, wear full-sleeved clothes.',
            'impact': 'Spreads rapidly in urban areas, high hospitalization rate.',
        },
        'typhoid': {
            'causes': 'Caused by Salmonella Typhi bacteria through contaminated food/water.',
            'prevention': 'Drink clean water, maintain hygiene.',
            'impact': 'Impacts sanitation-deficient areas most.',
        }
    }

    disease = disease.lower()
    if disease not in content:
        return HttpResponse("Invalid disease")

    context = {
        'disease': disease.title(),
        'report_id': report_id,
        'generated_at': generated_at,
        'causes': content[disease]['causes'],
        'prevention': content[disease]['prevention'],
        'impact': content[disease]['impact']
    }

    template = get_template('report_template.html')
    html = template.render(context)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"{disease}_report_{report_id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponse('Error generating PDF')