import streamlit as st
import pdfplumber
from docx import Document
import re

# --- Functions ---
def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded PDF file."""
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error extracting PDF text: {e}"

def extract_text_from_docx(uploaded_file):
    """Extracts text from an uploaded DOCX file."""
    try:
        doc = Document(uploaded_file)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        return f"Error extracting DOCX text: {e}"

def explain_clause_rule_based(legal_text):
    """Rule-based legal clause explanation without API."""
    
    # Dictionary of common legal terms and their explanations
    legal_glossary = {
        r'indemnify|hold harmless': 'You agree to protect someone else from losses or lawsuits',
        r'liability|liable': 'You can be held responsible or sued for something',
        r'warrant(y|ies)': 'You promise that something is true or will work a certain way',
        r'confidentiality|non-disclosure': 'You cannot share certain information with others',
        r'non-compete': 'You cannot work for competitors after leaving this job',
        r'terminat(e|ion)': 'How and when this agreement can be ended',
        r'arbitration': 'Disputes must be solved through private arbitration instead of court',
        r'jurisdiction|venue': 'Which state/court will handle any legal disputes',
        r'insurance|coverage': 'You need to have insurance protection',
        r'damages|compensation': 'Money that must be paid for losses or injuries',
        r'premises|property': 'Refers to the building or land being discussed',
        r'lessor|landlord': 'The property owner or manager',
        r'lessee|tenant': 'The person renting or using the property',
        r'default|breach': 'When someone fails to follow the agreement',
        r'remed(y|ies)': 'Solutions or fixes for problems that occur'
    }
    
    # Detect clause type and provide tailored explanation
    clause_type = "general"
    detected_terms = []
    
    for pattern, explanation in legal_glossary.items():
        if re.search(pattern, legal_text, re.IGNORECASE):
            detected_terms.append(explanation)
    
    # Generate explanation based on detected terms
    if not detected_terms:
        explanation = """
        **Simple Explanation:** 
        This clause contains various legal terms that create specific rights and responsibilities.
        
        **What This Means For You:** 
        You should carefully review this section as it may contain important obligations, restrictions, or potential costs.
        
        **Consider Asking:** 
        Ask for specific examples of how this clause would apply in practice, and whether any terms can be negotiated or clarified.
        """
    else:
        simple_explanation = "This clause covers: " + "; ".join(detected_terms[:3]) + "."
        
        what_it_means = "This means you may have specific responsibilities or restrictions. "
        if any('insurance' in term for term in detected_terms):
            what_it_means += "You might need to purchase insurance coverage. "
        if any('liable' in term for term in detected_terms):
            what_it_means += "You could be financially responsible for certain situations. "
        if any('non-compete' in term for term in detected_terms):
            what_it_means += "Your future employment options could be limited. "
        
        consider_asking = "Consider asking: What are specific examples of how this applies? "
        consider_asking += "Can any terms be modified? What are the consequences if this is violated?"
        
        explanation = f"""
        **Simple Explanation:** 
        {simple_explanation}
        
        **What This Means For You:** 
        {what_it_means}
        
        **Consider Asking:** 
        {consider_asking}
        """
    
    # Add detected terms list
    if detected_terms:
        explanation += f"\n\n**Key Terms Detected:**\n" + "\n".join([f"• {term}" for term in detected_terms])
    
    return explanation

# --- Streamlit UI ---
st.set_page_config(page_title="LexiGen - Demystify Legal Documents", page_icon="⚖️")
st.title("⚖️ LexiGen Prototype")
st.markdown("**Upload a legal document or paste text for plain-language explanation**")

# File upload
uploaded_file = st.file_uploader("Choose PDF or DOCX file", type=['pdf', 'docx'])
extracted_text = ""

if uploaded_file is not None:
    with st.spinner('Extracting text...'):
        if uploaded_file.type == "application/pdf":
            extracted_text = extract_text_from_pdf(uploaded_file)
        else:
            extracted_text = extract_text_from_docx(uploaded_file)

    if extracted_text and not extracted_text.startswith("Error"):
        st.success("✅ Text extracted! Select portion to analyze.")
        with st.expander("View extracted text"):
            st.text(extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text)
    elif extracted_text.startswith("Error"):
        st.error(extracted_text)

# Text input
clause_to_analyze = st.text_area(
    "**Paste legal clause here:**",
    height=150,
    value=extracted_text[:500] if extracted_text and not extracted_text.startswith("Error") else "",
    help="Paste any legal text you want explained in plain language"
)

# Sample texts
sample_options = {
    "Rental Agreement": "The tenant shall be responsible for all damages to the premises beyond normal wear and tear and shall maintain renter's insurance with a minimum coverage of $100,000 throughout the lease term.",
    "Employment Contract": "The employee agrees to a non-compete clause prohibiting employment with any direct competitors within a 50-mile radius for a period of 12 months following termination.",
    "Privacy Policy": "The company reserves the right to collect, store, and share user data including browsing history and personal information with third-party advertising partners."
}

sample_choice = st.selectbox("📋 Load Sample Text:", ["Select sample..."] + list(sample_options.keys()))

if sample_choice != "Select sample...":
    clause_to_analyze = sample_options[sample_choice]

# Analysis
if st.button("🧠 Analyze with AI", type="primary"):
    if clause_to_analyze.strip():
        with st.spinner('Analyzing clause...'):
            explanation = explain_clause_rule_based(clause_to_analyze)
        
        st.subheader("🤖 LexiGen's Analysis:")
        st.markdown(explanation)
        
        with st.expander("📜 View Original Clause"):
            st.text(clause_to_analyze)
    else:
        st.warning("⚠️ Please paste a legal clause into the text box")

# Footer
st.markdown("---")
st.markdown("**Built by Team LexiGen for GenAI Exchange Hackathon**")
st.markdown("*Privacy-First & Secure • No API Required • Fully Local*")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About LexiGen")
    st.markdown("""
    **AI-powered legal document simplification:**
    - 📖 Explains legal jargon in plain English
    - ⚠️ Highlights important obligations
    - 💡 Suggests questions to ask
    - 🔒 Processes text locally - no API needed
    """)
    st.markdown("---")
    st.markdown("**How to use:**")
    st.markdown("1. Upload file OR paste text")
    st.markdown("2. Click 'Analyze with AI'")
    st.markdown("3. Get instant explanation")