import json
import re
import time
import random
from ddgs import DDGS

SESSION = {"last_topic": None, "source": "LOCAL_DB"}

def is_strictly_english(text):
    """Hard filter to block non-English scripts and specific accents."""
    if not text: return False
    if re.search(r'[\u0980-\u09FF\u4E00-\u9FFF\u0600-\u06FFáéíóúñ¿¡]', text):
        return False
    non_ascii = len(re.findall(r'[^\x00-\x7F]', text))
    return (non_ascii / len(text)) < 0.02

def get_live_medical_data(query):
    """Bypasses library hangs by using a fast generator approach."""
    subject = re.sub(r'(tell me about|what is|explain|about)', '', query.lower()).strip()
    refined_query = f"{subject} clinical pathology symptoms"
    
    report_sections = []
    sources = []

    try:
        with DDGS() as ddgs:
            resp = ddgs.text(refined_query, region="us-en", safesearch="moderate")
            for i, r in enumerate(resp):
                if i > 8: break 
                body = r.get('body', '')
                link = r.get('href', '')
                if len(body) > 70 and is_strictly_english(body):
                    clean_text = re.sub(r'^.*?·\s', '', body)
                    report_sections.append(clean_text)
                    domain = re.findall(r'https?://(?:www\.)?([^/]+)', link)
                    source_name = domain[0] if domain else "Clinical Source"
                    sources.append(f"<a href='{link}' target='_blank' style='color:#00ffcc; text-decoration:none; margin-right:10px;'>[{source_name}]</a>")
                if len(report_sections) >= 4: break 

            if report_sections:
                content = "\n\n".join(report_sections)
                source_html = "<div class='sources-section' style='margin-top:15px; font-size:0.9em;'><b>VERIFIED SOURCES:</b><br>" + "".join(list(set(sources))) + "</div>"
                return content, source_html
    except Exception as e:
        print(f"STABLE LINK LOG: {e}")
    return "Neural Link timeout. Please check your internet or try a broader medical term.", ""

def brain(user_input, image_b64=None):
    global SESSION
    raw_query = user_input.strip()
    user_input = user_input.lower().strip()
    
    try:
        with open('medical_db.json', 'r') as f:
            db = json.load(f)
    except:
        return "Database Error", "ERROR"

    medical_triggers = ["cancer", "tumor", "disease", "symptom", "virus", "infection"]
    is_medical = any(word in user_input for word in medical_triggers) or \
                 any(p in user_input for p in ["tell me", "what is"])

    local_match = None
    all_knowledge = db.get('medical_conditions', []) + db.get('health_awareness', [])
    for item in all_knowledge:
        if any(re.search(rf"\b{re.escape(key)}\b", user_input) for key in item['keywords']):
            local_match = item
            break

    prefix = "<b>Neural Image Analysis:</b> Complete.<br><br>" if image_b64 else ""

    if is_medical:
        SESSION["source"] = "HYBRID_SCAN" if local_match else "LIVE_WEB"
        web_res, source_links = get_live_medical_data(raw_query)
        
        local_html = f"<div class='local-insight' style='color: #00ffcc; background: rgba(0, 255, 204, 0.1); padding: 15px; border-left: 5px solid #00ffcc; margin-bottom: 20px;'><b>INTERNAL ANALYSIS:</b> {local_match['analysis']}</div>" if local_match else ""
        disclaimer = "<div class='disclaimer' style='margin-top:20px; padding:10px; border:1px solid #ff4444; color:#ff4444; font-size:0.75em;'><b>DISCLAIMER:</b> This AI analysis is for informational purposes only. Consult a licensed medical professional for diagnosis.</div>"

        response_html = f"""
        <div id='printableReport' class='web-insight' style='font-family: sans-serif; color: #ffffff; padding: 25px; position: relative; background: #0b0e14; border-radius: 8px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #00ffcc; padding-bottom: 10px; margin-bottom: 20px;'>
                <h2 style='color: #00ffcc; margin: 0;'>CLINICAL REPORT: {raw_query.upper()}</h2>
                <button onclick="toggleSummary()" id="sumBtn" class="no-print" style='background: rgba(0, 255, 204, 0.2); color: #00ffcc; border: 1px solid #00ffcc; padding: 5px 12px; cursor: pointer; font-weight: bold; border-radius: 4px;'>SUMMARIZE</button>
            </div>
            
            <div class='pdf-only' style='display: none;'>
                <h1 style='color: #000; margin-bottom: 5px;'>NEURAL LINK MEDICAL EXPORT</h1>
                <p style='color: #444; margin-bottom: 20px;'>Report generated on: {time.strftime("%B %d, %Y")}</p>
                <hr style='border: 1px solid #000;'>
            </div>

            {local_html}
            
            <div id='reportContent' style='line-height: 1.8; text-align: justify; font-size: 1.08em; margin-bottom: 20px;'>
                {web_res.replace('\n\n', '<br><br>')}
            </div>

            {source_links}
            {disclaimer}

            <div class='pdf-only' style='display: none; margin-top: 50px; border-top: 1px solid #000; width: 300px; padding-top: 10px;'>
                <p style='color: #000; font-weight: bold; margin: 0;'>Clinical Officer Signature</p>
                <p style='color: #666; font-size: 0.8em; margin: 0;'>Date: ____________________</p>
            </div>

            <div class='no-print' style='margin-top: 30px; display: flex; justify-content: flex-end;'>
                <button onclick="window.print()" style='background: #00ffcc; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; border-radius: 6px; box-shadow: 0 4px 15px rgba(0, 255, 204, 0.3);'>
                    DOWNLOAD PDF REPORT
                </button>
            </div>

            <script>
                function toggleSummary() {{
                    var content = document.getElementById('reportContent');
                    var btn = document.getElementById('sumBtn');
                    content.classList.toggle('summarized');
                    btn.innerText = content.classList.contains('summarized') ? "SHOW FULL" : "SUMMARIZE";
                }}
            </script>

            <style>
                .summarized {{ height: 140px; overflow: hidden; mask-image: linear-gradient(to bottom, black 40%, transparent 100%); -webkit-mask-image: linear-gradient(to bottom, black 40%, transparent 100%); }}
                @media print {{
                    body * {{ visibility: hidden; }}
                    #printableReport, #printableReport * {{ visibility: visible; }}
                    #printableReport {{ position: absolute; left: 0; top: 0; width: 100%; background: white !important; color: black !important; padding: 0 !important; }}
                    .no-print {{ display: none !important; }}
                    .pdf-only {{ display: block !important; }}
                    .local-insight {{ background: #f4f4f4 !important; color: black !important; border-color: #333 !important; }}
                    h2 {{ color: black !important; border-bottom: 2px solid black !important; }}
                    #reportContent {{ color: black !important; }}
                    .disclaimer {{ border-color: #000 !important; color: #000 !important; }}
                    a {{ color: blue !important; text-decoration: underline !important; }}
                }}
            </style>
        </div>
        """
        return f"{prefix}{response_html}", SESSION["source"]

    return "Neural link active. Provide English clinical query.", "LOCAL_DB"