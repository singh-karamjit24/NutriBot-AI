# 🥗 NutriMed AI — Intelligent Diet, Food & Medical Assistant

**NutriMed AI** is an all-in-one health and nutrition app built with **Streamlit**, designed to help users create personalized diet plans, explore healthy recipes, and learn about diseases — all with interactive charts and downloadable reports.

---

## 🚀 Features

### 🧮 1. Weekly Diet & Routine Planner
- Generates a **7-day personalized meal plan** based on:
  - Age, gender, height, weight, and activity level  
  - Fitness goals (weight loss, gain, or maintenance)  
  - Dietary preferences (vegetarian / non-vegetarian)
- Calculates **BMI** and **daily calorie requirements**
- Visualizes data using **Plotly** charts:
  - Calorie distribution (line chart)
  - Day-wise meal distribution (pie charts)
- Exports a **beautiful PDF report** with the complete plan and daily routine

---

### 🍴 2. Food Chatbot
- Type what you feel like eating — e.g., *“spicy paneer”*, *“sweet dessert”*, or *“healthy lunch”*  
- AI filters and recommends recipes from `recipes.json`
- Displays:
  - Description  
  - Ingredients and steps  
  - Food images  
- Provides **“Order Online”** links for Zomato, Swiggy, and Google Search

---

### 🩺 3. Medical Chatbot
- Search or browse diseases from `medical.json`
- Displays information on:
  - Definition  
  - Symptoms  
  - Treatment  
  - Prevention  
- Download **disease info reports** as PDF files

---

## 🧰 Tech Stack
| Component | Technology |
|------------|-------------|
| Frontend/UI | Streamlit |
| Data Handling | Pandas, JSON |
| Visualization | Plotly |
| Report Generation | ReportLab |
| Language | Python 3.10+ |

---

## 📁 Project Structure
NutriMed-AI/
│
├── diet_app.py # Main Streamlit application
├── recipes.json # Recipe dataset
├── medical.json # Disease information dataset
├── images/ # Icons and brand logos (Zomato, Swiggy, Google)
