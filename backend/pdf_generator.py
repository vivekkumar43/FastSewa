import jinja2
import pdfkit
import os
from datetime import datetime

# =============================================
# CONFIGURATION
# =============================================

# Path to wkhtmltopdf executable
PATH_WKHTMLTOPDF = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=PATH_WKHTMLTOPDF)

# Output directory for PDFs
OUTPUT_DIR = "generated_pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================
# SERVICE MAPPING
# =============================================

def get_service_name(code):
    """Maps service codes to full names"""
    mapping = {
        "FS_BUILD": "Construction (FastSewa BuildNet)",
        "FS_SECURE": "Security Services (SecureForce)",
        "FS_LEGAL": "Legal & GST Services (Filings)",
        "FS_MEDICAL": "Medical Services",
        "FS_LAND": "Land Verification",
        "FS_REPAIR": "Repair & Maintenance"
    }
    return mapping.get(code, "General Service")

# =============================================
# MAIN PDF GENERATION FUNCTION
# =============================================

def generate_invoice(user_data, enquiry_data):
    """
    Generates professional PDF invoice/quote
    
    Args:
        user_data (dict): Customer information
            - full_name: str
            - phone: str
            - address: str
            
        enquiry_data (dict): Service request details
            - id: int/str (unique identifier)
            - service_type: str (FS_BUILD, FS_SECURE, etc.)
            - form_data: dict with service-specific details
    
    Returns:
        str: Success/error message with filename
    """
    
    try:
        # 1. Setup Jinja2 Template Environment
        current_directory = os.path.dirname(os.path.abspath(__file__))
        template_loader = jinja2.FileSystemLoader(current_directory)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template('invoice_template.html')
        
        # 2. Extract and validate data
        forms = enquiry_data.get('form_data', {})
        enquiry_id = enquiry_data.get('id', 'UNKNOWN')
        service_code = enquiry_data.get('service_type', 'GENERAL')
        
        # 3. Prepare context for HTML rendering
        context = {
            'customer_name': user_data.get('full_name', 'Valued Customer'),
            'customer_phone': user_data.get('phone', 'Not Provided'),
            'customer_address': user_data.get('address', 'Not Provided'),
            'quote_id': f"FS-{enquiry_id}",
            'date': datetime.now().strftime("%d %B %Y"),
            'time': datetime.now().strftime("%I:%M %p"),
            'service_category': get_service_name(service_code),
            'service_description': forms.get('requirements', 'Standard Service Request'),
            'amount': forms.get('budget_range', 'Estimate on Request'),
            'total_amount': forms.get('budget_range', 'To Be Confirmed'),
            
            # Additional service-specific details
            'plot_area': forms.get('plot_area', 'N/A'),
            'property_type': forms.get('property_type', 'N/A'),
            'guard_count': forms.get('guard_count', 'N/A'),
            'symptoms': forms.get('symptoms', 'N/A')
        }
        
        # 4. Render HTML from template
        output_html = template.render(context)
        
        # 5. Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"FastSewa_Quote_{enquiry_id}_{timestamp}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # 6. Convert HTML to PDF
        pdfkit.from_string(
            output_html, 
            filepath, 
            configuration=config,
            options={
                'page-size': 'A4',
                'margin-top': '0.5in',
                'margin-right': '0.5in',
                'margin-bottom': '0.5in',
                'margin-left': '0.5in',
                'encoding': "UTF-8",
                'enable-local-file-access': None
            }
        )
        
        return f"✅ PDF Created Successfully: {filename}\n📄 Location: {filepath}"
        
    except FileNotFoundError:
        return "❌ Error: invoice_template.html not found. Please ensure template file is in the same directory."
    
    except Exception as e:
        return f"❌ PDF Generation Failed: {str(e)}\n💡 Tip: Check wkhtmltopdf installation and path."

# =============================================
# UTILITY FUNCTION (Optional - for bulk generation)
# =============================================

def generate_bulk_invoices(enquiries_list):
    """
    Generate multiple PDFs in batch
    
    Args:
        enquiries_list: List of (user_data, enquiry_data) tuples
    
    Returns:
        dict: Summary of successes and failures
    """
    results = {"success": [], "failed": []}
    
    for user_data, enquiry_data in enquiries_list:
        result = generate_invoice(user_data, enquiry_data)
        
        if "✅" in result:
            results["success"].append(enquiry_data.get('id'))
        else:
            results["failed"].append(enquiry_data.get('id'))
    
    return results

# =============================================
# TEST BLOCK
# =============================================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🧪 PDF GENERATOR TEST")
    print("="*50 + "\n")
    
    # Test Case 1: Construction Service
    test_user = {
        'full_name': 'Rajesh Kumar',
        'phone': '+91-9876543210',
        'address': 'Sector 15, Chandigarh'
    }
    
    test_enquiry = {
        'id': 1001,
        'service_type': 'FS_BUILD',
        'form_data': {
            'requirements': '3BHK Residential Construction',
            'budget_range': '₹50-60 Lakhs',
            'plot_area': '2000 sqft'
        }
    }
    
    print("Test 1: Construction Service")
    result = generate_invoice(test_user, test_enquiry)
    print(result)
    
    print("\n" + "-"*50 + "\n")
    
    # Test Case 2: Security Service
    test_enquiry_2 = {
        'id': 1002,
        'service_type': 'FS_SECURE',
        'form_data': {
            'requirements': '2 Guards for Residential Society',
            'budget_range': '₹25,000/month',
            'property_type': 'Residential',
            'guard_count': '2'
        }
    }
    
    print("Test 2: Security Service")
    result2 = generate_invoice(test_user, test_enquiry_2)
    print(result2)
    
    print("\n" + "="*50)
