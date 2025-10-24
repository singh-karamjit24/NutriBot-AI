import os
import random
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

# ----------------------------- Data -----------------------------
BASE_DIR = os.path.dirname(__file__) if "__file__" in globals() else "."
IMAGE_DIR = os.path.join(BASE_DIR, "images")
RECIPES_PATH = os.path.join(BASE_DIR, "recipes.json")
MEDICAL_PATH = os.path.join(BASE_DIR, "medical.json")
with open(RECIPES_PATH, "r", encoding="utf-8") as f:
    RECIPES = json.load(f)

with open(MEDICAL_PATH, "r", encoding="utf-8") as f:
    disease_info = json.load(f)

STOPWORDS = {"what","i","want","to","eat","give","me","please","can","have","some","the","a","an","for","need","show"}

# ----------------------------- PDF Generation Functions -----------------------------
def create_diet_plan_pdf(calories, weekly_plan, bmi_data):
    """Generate PDF for weekly diet plan"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    story = []
    
    # Title
    story.append(Paragraph("🥗 Weekly Diet & Routine Plan", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Summary
    story.append(Paragraph(f"<b>Daily Calorie Requirement:</b> {calories} kcal", styles['Normal']))
    story.append(Paragraph(f"<b>BMI:</b> {bmi_data['value']} ({bmi_data['category']})", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Weekly Plan
    for day, plan_data in weekly_plan.items():
        story.append(Paragraph(f"<b>{day}</b>", heading_style))
        
        # Meals Table
        meal_data = [['Meal', 'Dish', 'Calories']]
        for meal, details in plan_data['meals'].items():
            meal_data.append([meal, details['dish'], f"{details['calories']} kcal"])
        
        meal_table = Table(meal_data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
        meal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(meal_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Routine
        story.append(Paragraph("<b>Daily Routine:</b>", styles['Normal']))
        for tip in plan_data['routine']:
            story.append(Paragraph(f"• {tip}", styles['Normal']))
        
        story.append(Paragraph(f"<b>Total Calories:</b> {plan_data['total_calories']} kcal", styles['Normal']))
        story.append(PageBreak())
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_disease_info_pdf(disease_name, info):
    """Generate PDF for disease information"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#E74C3C'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#C0392B'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    story = []
    
    # Title
    story.append(Paragraph(f"🩺 {disease_name}", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Definition
    story.append(Paragraph("📖 Definition", heading_style))
    story.append(Paragraph(info.get("definition", "No definition available."), styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Symptoms
    story.append(Paragraph("⚠️ Symptoms", heading_style))
    if info.get("symptoms"):
        for symptom in info["symptoms"]:
            story.append(Paragraph(f"• {symptom}", styles['Normal']))
    else:
        story.append(Paragraph("No symptoms information available.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Treatment
    story.append(Paragraph("💊 Treatment", heading_style))
    if info.get("treatment"):
        for treatment in info["treatment"]:
            story.append(Paragraph(f"• {treatment}", styles['Normal']))
    else:
        story.append(Paragraph("No treatment information available.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Prevention
    story.append(Paragraph("🛡️ Prevention", heading_style))
    if info.get("prevention"):
        for prevention in info["prevention"]:
            story.append(Paragraph(f"• {prevention}", styles['Normal']))
    else:
        story.append(Paragraph("No prevention information available.", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ----------------------------- Helper Functions -----------------------------
def parse_diet_query(text):
    text = (text or "").lower().strip()
    if not text: return []
    words = [w for w in text.split() if w not in STOPWORDS and len(w)>1]
    matches = [r["title"] for r in RECIPES if any(w in r["title"].lower() for w in words)]
    if not matches:
        import difflib
        fuzzy = difflib.get_close_matches(text, [r["title"].lower() for r in RECIPES], n=6, cutoff=0.5)
        matches.extend([f.title() for f in fuzzy])
    return list(dict.fromkeys(matches))[:6]

def calculate_calories(age, gender, weight, height, activity_level, goal):
    if gender=="male":
        bmr = 88.362 + (13.397*weight) + (4.799*height) - (5.677*age)
    else:
        bmr = 447.593 + (9.247*weight) + (3.098*height) - (4.330*age)
    factors={"sedentary":1.2,"light":1.375,"moderate":1.55,"active":1.725,"very active":1.9}
    calories=bmr*factors.get(activity_level,1.2)
    if goal=="weight_loss": calories-=500
    elif goal=="weight_gain": calories+=500
    return round(calories)

def calculate_bmi(weight,height_cm):
    h=height_cm/100
    bmi=round(weight/(h**2),1)
    if bmi<18.5: cat="Underweight"
    elif bmi<25: cat="Normal weight"
    elif bmi<30: cat="Overweight"
    else: cat="Obese"
    return bmi,cat

def generate_meal_plan(preference="vegetarian"):
    meals = {
        "vegetarian": {
            "Breakfast":[("Oats + banana",350),("Poha",300),("Paneer paratha",400)],
            "Lunch":[("Brown rice + dal",500),("Chapati + paneer curry",550),("Quinoa + veg curry",480)],
            "Snack":[("Apple + almonds",200),("Smoothie",250),("Roasted chickpeas",220)],
            "Dinner":[("Khichdi + salad",400),("Tofu curry + rice",450),("Moong dal cheela",380)]
        },
        "non-vegetarian": {
            "Breakfast":[("Boiled eggs + toast",350),("Oats + milk + egg",370),("Chicken sandwich",400)],
            "Lunch":[("Grilled chicken + rice",600),("Fish curry + chapati",550),("Egg curry + quinoa",520)],
            "Snack":[("Greek yogurt + berries",250),("Protein shake",300),("Boiled egg + apple",220)],
            "Dinner":[("Grilled fish + salad",450),("Chicken curry + rice",550),("Omelette + veggies",400)]
        }
    }
    plan,total={},0
    for meal,opts in meals[preference].items():
        dish,cal=random.choice(opts)
        plan[meal]={"dish":dish,"calories":cal}
        total+=cal
    return plan,total

def weekly_routine(goal):
    routines={
        "weight_loss":[["30-min walk","3L water","Sleep 7-8 hrs","Meditation 15 min"]]*7,
        "weight_gain":[["Strength training","High-protein snacks","Hydration 3L","Sleep 8 hrs"]]*7,
        "maintenance":[["Balanced workout","2.5L water","Sleep 7-8 hrs","Stretch"]]*7
    }
    return routines.get(goal,routines["maintenance"])

# ----------------------------- Pages -----------------------------
def home_page():
    st.title("🍽️ NutriMed AI")
    st.write("Select a feature below:")
    st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 100px;
        font-size: 100px;
        font-weight: bold;
        border-radius: 15px;
        box-shadow: 2px 2px 10px #aaa;
        transition: 0.3s;
        margin-bottom: 10px;
        margin-left:150px
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background-color: #e0f7fa;
        font-color:#eeffa;
        box-shadow: 4px 4px 20px #888;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("\t🥗 Diet & Routine Planner"):
        st.session_state["page"] = "diet"
    if st.button("\t      🍴 Food Chatbot    "):
        st.session_state["page"] = "food_chat"
    if st.button("\t     🩺 Medical Chatbot  "):
        st.session_state["page"] = "medical_chat"
        

def diet_planner_page():
    st.header("🥗 Weekly Diet & Routine Planner")
    if st.button("⬅️ Home"): st.session_state["page"]="home"
    age = st.number_input("Age",10,100,25)
    gender = st.radio("Gender",["Male","Female"]).lower()
    weight = st.number_input("Weight (kg)",30.0,200.0,70.0)
    height = st.number_input("Height (cm)",100.0,220.0,170.0)
    activity_level = st.selectbox("Activity Level",["Sedentary","Light","Moderate","Active","Very Active"]).lower()
    goal = st.selectbox("Goal",["Weight Loss","Weight Gain","Maintenance"]).replace(" ","_").lower()
    preference = st.radio("Diet Preference",["vegetarian","non-vegetarian"])

    if st.button("Generate Weekly Plan"):
        calories = calculate_calories(age,gender,weight,height,activity_level,goal)
        st.success(f"🔥 Daily Calorie Requirement: {calories} kcal")
        bmi_value,bmi_cat=calculate_bmi(weight,height)
        routines=weekly_routine(goal)
        weekly_plan,daily_totals={},[]

        tab1,tab2,tab3,tab4=st.tabs(["🍴 Meals","💪 Routine","📊 Charts","⚖️ BMI"])
        with tab1:
            st.subheader("7-Day Meal Plans")
            for day in range(1,8):
                plan,total_cals=generate_meal_plan(preference)
                weekly_plan[f"Day {day}"]={"meals":plan,"routine":routines[day-1],"total_calories":total_cals}
                daily_totals.append({"Day":f"Day {day}","Calories":total_cals})
                st.markdown(f"### 📅 Day {day}")
                cols=st.columns(4)
                for i,(meal,details) in enumerate(plan.items()):
                    with cols[i]:
                        st.metric(label=meal,value=f"{details['calories']} kcal")
                        st.write(details["dish"])

        with tab2:
            st.subheader("7-Day Routine Plan")
            for day in range(1,8):
                st.markdown(f"### 📅 Day {day}")
                for tip in routines[day-1]: st.write(f"- {tip}")

        with tab3:
            st.subheader("📊 Weekly Calorie Distribution")
            df=pd.DataFrame(daily_totals)
            fig_line=px.line(df,x="Day",y="Calories",markers=True)
            st.plotly_chart(fig_line,use_container_width=True)
            st.subheader("🍽️ Day-wise Meal Calorie Pie")
            for day in range(1,8):
                plan=weekly_plan[f"Day {day}"]["meals"]
                labels=[m for m in plan.keys()]
                values=[plan[m]["calories"] for m in plan.keys()]
                fig=px.pie(names=labels,values=values,title=f"Day {day} Meal Distribution")
                st.plotly_chart(fig,use_container_width=True)

        with tab4:
            st.subheader("⚖️ BMI")
            st.write(f"**Your BMI:** {bmi_value} ({bmi_cat})")

            fig=go.Figure(go.Indicator(
                mode="gauge+number",
                value=bmi_value,
                gauge={'axis': {'range':[0,50]},
                       'bar':{'color':'black'},
                       'steps':[{'range':[0,18.5],'color':'#3498db'},
                                {'range':[18.5,25],'color':'#2ecc71'},
                                {'range':[25,30],'color':'#e67e22'},
                                {'range':[30,50],'color':'#e74c3c'}],
                       'threshold':{'line':{'color':'black','width':4},'thickness':0.75,'value':bmi_value}}))
            st.plotly_chart(fig,use_container_width=True)

            if bmi_cat=="Underweight": st.info("You are underweight. Increase calories.")
            elif bmi_cat=="Normal weight": st.success("Healthy weight!")
            elif bmi_cat=="Overweight": st.warning("Overweight. Moderate diet & exercise.")
            else: st.error("Obese. Consult a professional.")

        # PDF Download Button (outside tabs, at the bottom)
        st.markdown("---")
        pdf_buffer = create_diet_plan_pdf(
            calories, 
            weekly_plan, 
            {"value": bmi_value, "category": bmi_cat}
        )
        st.download_button(
            "📥 Download Weekly Plan (PDF)",
            pdf_buffer,
            "weekly_diet_plan.pdf",
            "application/pdf",
            key="diet_pdf_download"
        )

def food_chatbot_page():
    st.header("🤖 Food Chatbot")
    if st.button("⬅️ Home"): st.session_state["page"] = "home"

    typed = st.text_input("Type what you want to eat (e.g., 'spicy', 'sweet', 'Paneer Tikka'):")

    if typed:
        typed_lower = typed.lower().strip()

        # Taste/diet keywords
        taste_keywords = ["spicy", "sweet", "savory", "healthy"]
        diet_keywords = ["vegetarian", "non-vegetarian"]

        if any(k in typed_lower for k in taste_keywords + diet_keywords):
            preference = st.radio(
                "Select diet preference:",
                ["vegetarian", "non-vegetarian", "both"],
                horizontal=True
            )

            filtered_recipes = []
            for r in RECIPES:
                tag_match = any(k in r.get("tags", []) for k in typed_lower.split())
                diet_match = (preference == "both") or (r.get("diet") == preference)
                if tag_match and diet_match:
                    filtered_recipes.append(r)

            if filtered_recipes:
                for recipe in filtered_recipes:
                    st.subheader(recipe["title"])
                    # Columns: text left, image right
                    cols = st.columns([2,1])
                    with cols[0]:
                        st.write(recipe["description"])
                        st.write("**Ingredients:** " + ", ".join(recipe["ingredients"]))
                        st.write("**Steps:**")
                        for i, step in enumerate(recipe["steps"], 1):
                            st.write(f"{i}. {step}")

                        # Order Online Logos
                        st.markdown("### 🛒 Order Online:")
                        logo_cols = st.columns(3)
                        logos = {
                            "Zomato": ("zomato.png", f"https://www.zomato.com/search?q={recipe['title']}"),
                            "Swiggy": ("swiggy.png", f"https://www.swiggy.com/search?q={recipe['title']}"),
                            "Google": ("google.png", f"https://www.google.com/search?q=order+{recipe['title']}")
                        }
                        for i, (name, (logo_file, link)) in enumerate(logos.items()):
                            logo_path = os.path.join(IMAGE_DIR, logo_file)
                            if os.path.exists(logo_path):
                                with logo_cols[i]:
                                    with open(logo_path, "rb") as img_f:
                                        encoded = base64.b64encode(img_f.read()).decode()
                                    st.markdown(
                                        f'<a href="{link}" target="_blank">'
                                        f'<img src="data:image/png;base64,{encoded}" width="80">'
                                        f'</a>',
                                        unsafe_allow_html=True
                                    )
                    with cols[1]:
                        st.image(recipe.get("image", ""), use_container_width=True)
            else:
                st.info("⚠️ No recipes found for this preference.")
        else:
            # Normal dish search
            suggestions = parse_diet_query(typed)
            if suggestions:
                selected = st.selectbox("Did you mean:", suggestions)
                recipe = next((r for r in RECIPES if r["title"].lower() == selected.lower()), None)
                if recipe:
                    st.subheader(recipe["title"])
                    cols = st.columns([2,1])
                    with cols[0]:
                        st.write(recipe["description"])
                        st.write("**Ingredients:** " + ", ".join(recipe["ingredients"]))
                        st.write("**Steps:**")
                        for i, step in enumerate(recipe["steps"], 1):
                            st.write(f"{i}. {step}")

                        st.markdown("### 🛒 Order Online:")
                        logo_cols = st.columns(3)
                        logos = {
                            "Zomato": ("zomato.png", f"https://www.zomato.com/search?q={recipe['title']}"),
                            "Swiggy": ("swiggy.png", f"https://www.swiggy.com/search?q={recipe['title']}"),
                            "Google": ("google.png", f"https://www.google.com/search?q=order+{recipe['title']}")
                        }
                        for i, (name, (logo_file, link)) in enumerate(logos.items()):
                            logo_path = os.path.join(IMAGE_DIR, logo_file)
                            if os.path.exists(logo_path):
                                with logo_cols[i]:
                                    with open(logo_path, "rb") as img_f:
                                        encoded = base64.b64encode(img_f.read()).decode()
                                    st.markdown(
                                        f'<a href="{link}" target="_blank">'
                                        f'<img src="data:image/png;base64,{encoded}" width="80">'
                                        f'</a>',
                                        unsafe_allow_html=True
                                    )
                    with cols[1]:
                        st.image(recipe.get("image", ""), use_container_width=True)
            else:
                st.info("⚠️ No matching recipes found.")             

def medical_chatbot_page():
    if st.button("⬅️ Home"): st.session_state["page"] = "home"
    st.title("🩺 Medical Information Search")
    st.write("Search or browse for any disease to get definition, symptoms, treatment, and prevention.")

    disease_names = sorted(disease_info.keys())

    if "selected_disease" not in st.session_state:
        st.session_state.selected_disease = None

    typed = st.text_input("Type disease name (partial match supported)")
    if typed:
        filtered = [d for d in disease_names if typed.lower() in d.lower()]
        if filtered:
            st.session_state.selected_disease = st.selectbox("Select Disease", options=filtered)
        else:
            st.warning("No matching disease found.")
            st.session_state.selected_disease = None
    else:
        st.session_state.selected_disease = st.selectbox("Or browse all diseases", options=disease_names)

    disease = st.session_state.selected_disease
    if disease:
        info = disease_info[disease]

        if "image" in info:
            st.image(info["image"], use_container_width=True)

        tab1, tab2, tab3, tab4 = st.tabs(["Definition", "Symptoms", "Treatment", "Prevention"])
        with tab1:
            st.subheader("📖 Definition")
            st.write(info.get("definition", "No definition available."))

        with tab2:
            st.subheader("⚠️ Symptoms")
            if info.get("symptoms"):
                for s in info["symptoms"]:
                    st.write(f"- {s}")
            else:
                st.info("No symptoms information available.")

        with tab3:
            st.subheader("💊 Treatment")
            if info.get("treatment"):
                for t in info["treatment"]:
                    st.write(f"- {t}")
            else:
                st.info("No treatment information available.")

        with tab4:
            st.subheader("🛡️ Prevention")
            if info.get("prevention"):
                for p in info["prevention"]:
                    st.write(f"- {p}")
            else:
                st.info("No prevention information available.")

        # PDF Download Button
        pdf_buffer = create_disease_info_pdf(disease, info)
        st.download_button(
            "📥 Download Disease Info (PDF)",
            pdf_buffer,
            f"{disease}_info.pdf",
            "application/pdf"
        )

# ----------------------------- Main -----------------------------
if "page" not in st.session_state: st.session_state["page"]="home"
if st.session_state["page"]=="home": home_page()
elif st.session_state["page"]=="diet": diet_planner_page()
elif st.session_state["page"]=="food_chat": food_chatbot_page()
elif st.session_state["page"]=="medical_chat": medical_chatbot_page()