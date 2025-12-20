import json
import random
from datetime import datetime
import pdf_generator

# =============================================
# CONFIGURATION & DATA LOADING
# =============================================

with open('intents.json','r', encoding='utf-8') as file:
    data = json.load(file)
print("✅ FastSewa Chatbot System Loaded")

# =============================================
# MEMORY STORAGE
# =============================================

user_context = {}      # Tracks conversation flow state
user_data = {}         # Stores collected information
active_service = {}    # NEW: Explicitly tracks which service user selected

# =============================================
# SERVICE DEFINITIONS (The 6 Services)
# =============================================

SERVICES = {
    "FS_BUILD": "Construction (BuildNet)",
    "FS_SECURE": "Security Guards (SecureForce)",
    "FS_LEGAL": "Legal & GST (Filings)",
    "FS_MEDICAL": "Medical Services",
    "FS_LAND": "Land Verification",
    "FS_REPAIR": "Repair & Maintenance"
}

# =============================================
# HELPER FUNCTIONS
# =============================================

def reset_user_session(user_id):
    """Clean reset after PDF generation or error"""
    user_context[user_id] = None
    user_data[user_id] = {}
    active_service[user_id] = None

def validate_input(input_text, expected_type="text"):
    """Basic input validation with error handling"""
    input_text = input_text.strip()
    
    if not input_text:
        return False, "Please provide valid input."
    
    if expected_type == "number":
        # Extract numbers from text (e.g., "1500 sqft" → "1500")
        numbers = ''.join(filter(str.isdigit, input_text))
        if not numbers:
            return False, "Please provide a valid number (e.g., 1500 sqft)."
        return True, numbers
    
    if expected_type == "location":
        if len(input_text) < 3:
            return False, "Please provide a valid city/area name."
        return True, input_text.title()
    
    return True, input_text

# =============================================
# CORE CHATBOT LOGIC
# =============================================

def get_response(user_input, user_id='default'):
    """
    Main conversation handler with explicit service selection
    and guided context flow (Mentor's requirement)
    """
    
    user_input_lower = user_input.lower()
    current_context = user_context.get(user_id)
    current_service = active_service.get(user_id)
    
    # Initialize user storage if new
    if user_id not in user_data:
        user_data[user_id] = {}
    
    # ==========================================
    # CONTEXT-BASED FLOWS (Service-Specific)
    # ==========================================
    
    # --- CONSTRUCTION FLOW ---
    if current_service == "FS_BUILD":
        
        # Step 1: Waiting for plot size
        if current_context == 'waiting_for_plotsize':
            is_valid, result = validate_input(user_input, "number")
            if not is_valid:
                return f"❌ {result} Please try again (e.g., 1500 sqft)."
            
            user_data[user_id]['plot_size'] = result
            user_context[user_id] = 'waiting_for_location'
            return f"✅ Got it! Plot size: {result} sqft. Now, which city/area is this project in?"
        
        # Step 2: Waiting for location (FINAL STEP → Generate PDF)
        if current_context == 'waiting_for_location':
            is_valid, result = validate_input(user_input, "location")
            if not is_valid:
                return f"❌ {result}"
            
            user_data[user_id]['location'] = result
            
            # Generate PDF
            try:
                customer_info = {
                    'full_name': user_data[user_id].get('name', 'Guest User'),
                    'phone': user_data[user_id].get('phone', 'N/A'),
                    'address': result
                }
                
                enquiry_info = {
                    'id': random.randint(1000, 9999),
                    'service_type': 'FS_BUILD',
                    'form_data': {
                        'requirements': f"Construction Project - {user_data[user_id]['plot_size']} sqft in {result}",
                        'budget_range': 'As per estimate',
                        'plot_area': user_data[user_id]['plot_size']
                    }
                }
                
                pdf_result = pdf_generator.generate_invoice(customer_info, enquiry_info)
                reset_user_session(user_id)
                
                return (
                    f"🎉 Perfect! Your Construction quote is ready.\n\n"
                    f"{pdf_result}\n\n"
                    f"Our team will contact you within 24 hours. Need anything else?"
                )
                
            except Exception as e:
                reset_user_session(user_id)
                return f"⚠️ Error generating PDF: {str(e)}. Please try again or contact support."
    
    # --- SECURITY SERVICE FLOW ---
    if current_service == "FS_SECURE":
        
        if current_context == 'waiting_for_property_type':
            property_type = user_input.title()
            user_data[user_id]['property_type'] = property_type
            user_context[user_id] = 'waiting_for_guard_count'
            return f"✅ {property_type} security noted. How many guards do you need? (e.g., 1, 2, 3)"
        
        if current_context == 'waiting_for_guard_count':
            is_valid, result = validate_input(user_input, "number")
            if not is_valid:
                return f"❌ {result}"
            
            user_data[user_id]['guard_count'] = result
            user_context[user_id] = 'waiting_for_security_location'
            return f"✅ {result} guard(s) required. Which city/area?"
        
        if current_context == 'waiting_for_security_location':
            is_valid, result = validate_input(user_input, "location")
            if not is_valid:
                return f"❌ {result}"
            
            # Generate PDF for Security
            try:
                customer_info = {
                    'full_name': 'Guest User',
                    'phone': 'N/A',
                    'address': result
                }
                
                enquiry_info = {
                    'id': random.randint(1000, 9999),
                    'service_type': 'FS_SECURE',
                    'form_data': {
                        'requirements': f"{user_data[user_id]['guard_count']} guards for {user_data[user_id]['property_type']} in {result}",
                        'budget_range': 'As per contract'
                    }
                }
                
                pdf_result = pdf_generator.generate_invoice(customer_info, enquiry_info)
                reset_user_session(user_id)
                
                return f"🎉 Security quote generated!\n\n{pdf_result}\n\nOur team will reach out soon."
                
            except Exception as e:
                reset_user_session(user_id)
                return f"⚠️ Error: {str(e)}. Please try again."
    
    # --- MEDICAL SERVICE FLOW ---
    if current_service == "FS_MEDICAL":
        
        if current_context == 'waiting_for_symptoms':
            symptoms = user_input
            user_data[user_id]['symptoms'] = symptoms
            user_context[user_id] = 'waiting_for_medical_location'
            return f"✅ Noted: {symptoms}. Which location do you need the service?"
        
        if current_context == 'waiting_for_medical_location':
            is_valid, result = validate_input(user_input, "location")
            if not is_valid:
                return f"❌ {result}"
            
            # Generate Medical PDF
            try:
                customer_info = {
                    'full_name': 'Guest User',
                    'phone': 'N/A',
                    'address': result
                }
                
                enquiry_info = {
                    'id': random.randint(1000, 9999),
                    'service_type': 'FS_MEDICAL',
                    'form_data': {
                        'requirements': f"Medical assistance for: {user_data[user_id]['symptoms']}",
                        'budget_range': 'Consultation fee applies'
                    }
                }
                
                pdf_result = pdf_generator.generate_invoice(customer_info, enquiry_info)
                reset_user_session(user_id)
                
                return f"🎉 Medical service request created!\n\n{pdf_result}\n\nDoctor will contact you shortly."
                
            except Exception as e:
                reset_user_session(user_id)
                return f"⚠️ Error: {str(e)}. Please contact emergency services if urgent."
    
    # ==========================================
    # INTENT MATCHING (Service Selection)
    # ==========================================
    
    for intent in data['intents']:
        for pattern in intent['patterns']:
            if pattern.lower() in user_input_lower:
                
                # Set context if specified in intent
                if 'context_set' in intent:
                    user_context[user_id] = intent['context_set']
                    
                    # Explicitly set active service based on tag
                    if 'construction' in intent['tag']:
                        active_service[user_id] = "FS_BUILD"
                    elif 'security' in intent['tag']:
                        active_service[user_id] = "FS_SECURE"
                    elif 'medical' in intent['tag']:
                        active_service[user_id] = "FS_MEDICAL"
                    elif 'legal' in intent['tag']:
                        active_service[user_id] = "FS_LEGAL"
                    elif 'land' in intent['tag']:
                        active_service[user_id] = "FS_LAND"
                    elif 'repair' in intent['tag']:
                        active_service[user_id] = "FS_REPAIR"
                
                return random.choice(intent['responses'])
    
    # ==========================================
    # FALLBACK HANDLER (Error Handling)
    # ==========================================
    
    return (
        "🤔 I didn't quite understand that.\n\n"
        "I can help with:\n"
        "• Construction quotes\n"
        "• Security guards\n"
        "• Medical services\n"
        "• Legal & GST\n"
        "• Land verification\n"
        "• Repair & maintenance\n\n"
        "Which service do you need?"
    )

# =============================================
# CHAT INTERFACE
# =============================================

if __name__ == "__main__":
    print("\n🤖 FastSewa Smart Assistant")
    print("=" * 50)
    print("Type 'quit' to exit\n")
    
    while True:
        user_in = input("You: ").strip()
        
        if user_in.lower() in ['quit', 'exit', 'bye']:
            print("Bot: Thank you for using FastSewa! Have a great day! 👋")
            break
        
        if not user_in:
            print("Bot: Please type something to continue.")
            continue
        
        response = get_response(user_in)
        print(f"Bot: {response}\n")
